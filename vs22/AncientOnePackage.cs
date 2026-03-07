using System;
using System.ComponentModel.Design;
using System.Reflection;
using System.Runtime.InteropServices;
using System.Threading;
using Microsoft.VisualStudio.Shell;
using Microsoft.VisualStudio.Shell.Interop;
using Task = System.Threading.Tasks.Task;

namespace InaVsTheme
{
    [PackageRegistration(UseManagedResourcesOnly = true, AllowsBackgroundLoading = true)]
    [ProvideMenuResource("Menus.ctmenu", 1)]
    [Guid(PackageGuidString)]
    public sealed class AncientOnePackage : AsyncPackage
    {
        public const string PackageGuidString = "a1b2c3d4-e5f6-7890-abcd-1234567890ab";

        public static readonly Guid CommandSetGuid = new Guid("b2c3d4e5-f6a7-8901-bcde-2345678901bc");

        private const int CmdIdDark = 0x0100;
        private const int CmdIdDarkViolet = 0x0101;
        private const int CmdIdDarkSlate = 0x0102;

        private static readonly (int cmdId, string themeGuid)[] Themes = new[]
        {
            (CmdIdDark,       "{6e3a4f5b-8c2d-4a91-b7e0-1f9d3c5a2b80}"),
            (CmdIdDarkViolet, "{7f4b5a6c-9d3e-4b02-c8f1-2a0e4d6b3c91}"),
            (CmdIdDarkSlate,  "{8a5c6b7d-0e4f-4c13-d902-3b1f5e7c4da2}"),
        };

        protected override async Task InitializeAsync(CancellationToken cancellationToken, IProgress<ServiceProgressData> progress)
        {
            await JoinableTaskFactory.SwitchToMainThreadAsync(cancellationToken);

            var commandService = await GetServiceAsync(typeof(IMenuCommandService)) as OleMenuCommandService;
            if (commandService == null)
                return;

            foreach (var (cmdId, themeGuid) in Themes)
            {
                var menuCommandId = new CommandID(CommandSetGuid, cmdId);
                var captured = themeGuid;
                var menuItem = new MenuCommand((s, e) => SwitchTheme(captured), menuCommandId);
                commandService.AddCommand(menuItem);
            }
        }

        private void SwitchTheme(string themeGuidStr)
        {
            ThreadHelper.ThrowIfNotOnUIThread();

            if (SwitchThemeViaColorThemeService(themeGuidStr))
            {
                ClearFontAndColorCaches();
            }
        }

        private bool SwitchThemeViaColorThemeService(string themeGuidStr)
        {
            ThreadHelper.ThrowIfNotOnUIThread();
            try
            {
                var guid = new Guid(themeGuidStr);

                Assembly windowManagement = null;
                foreach (var asm in AppDomain.CurrentDomain.GetAssemblies())
                {
                    if (asm.GetName().Name == "Microsoft.VisualStudio.Platform.WindowManagement")
                    {
                        windowManagement = asm;
                        break;
                    }
                }
                if (windowManagement == null) return false;

                var serviceType = windowManagement.GetType("Microsoft.VisualStudio.Platform.WindowManagement.ColorThemeService");
                if (serviceType == null) return false;

                var service = serviceType.GetProperty("Instance",
                    BindingFlags.Static | BindingFlags.Public | BindingFlags.NonPublic)?.GetValue(null);
                if (service == null) return false;

                var themes = serviceType.GetProperty("Themes",
                    BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic)?.GetValue(service);
                if (themes == null) return false;

                var getThemeMethod = themes.GetType().GetMethod("GetThemeFromId",
                    BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic);
                if (getThemeMethod == null) return false;

                var theme = getThemeMethod.Invoke(themes, new object[] { guid });
                if (theme == null) return false;

                var setMethod = serviceType.GetMethod("SetCurrentTheme",
                    BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic,
                    null,
                    new[] { getThemeMethod.ReturnType, typeof(bool), typeof(bool) },
                    null);
                if (setMethod == null) return false;

                setMethod.Invoke(service, new object[] { theme, true, true });
                return true;
            }
            catch
            {
                return false;
            }
        }

        private void ClearFontAndColorCaches()
        {
            ThreadHelper.ThrowIfNotOnUIThread();

            var cacheManager = GetService(typeof(SVsFontAndColorCacheManager)) as IVsFontAndColorCacheManager;
            if (cacheManager != null)
                cacheManager.ClearAllCaches();

            var storage = GetService(typeof(SVsFontAndColorStorage)) as IVsFontAndColorStorage;
            if (storage != null)
            {
                var textEditorCategory = new Guid("{A27B4E24-A735-4d1d-B8E7-9716E1E3D8E0}");
                var outputWindowCategory = new Guid("{9973EFDF-317D-431C-8BC1-5E88CBFD4F7F}");

                const uint flags = 0x2 | 0x8;
                var categories = new[] { textEditorCategory, outputWindowCategory };
                for (int i = 0; i < categories.Length; i++)
                {
                    var cat = categories[i];
                    if (storage.OpenCategory(ref cat, flags) == 0)
                        storage.CloseCategory();
                }
            }

            if (cacheManager != null)
                cacheManager.ClearAllCaches();
        }
    }
}
