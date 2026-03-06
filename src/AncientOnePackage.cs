using System;
using System.ComponentModel.Design;
using System.IO;
using System.Runtime.InteropServices;
using System.Text.RegularExpressions;
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

        // Command set GUID must match the .vsct
        public static readonly Guid CommandSetGuid = new Guid("b2c3d4e5-f6a7-8901-bcde-2345678901bc");

        // Command IDs must match the .vsct
        private const int CmdIdDark = 0x0100;
        private const int CmdIdDarkViolet = 0x0101;
        private const int CmdIdDarkSlate = 0x0102;

        // VS 2026 uses GUID-based slugs for extension themes
        private static readonly (int cmdId, string themeSlug)[] Themes = new[]
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

            foreach (var (cmdId, themeSlug) in Themes)
            {
                var menuCommandId = new CommandID(CommandSetGuid, cmdId);
                var captured = themeSlug;
                var menuItem = new MenuCommand((s, e) => SwitchTheme(captured), menuCommandId);
                commandService.AddCommand(menuItem);
            }
        }

        private void SwitchTheme(string themeSlug)
        {
            ThreadHelper.ThrowIfNotOnUIThread();

            string settingsPath = GetSettingsJsonPath();
            if (settingsPath == null || !File.Exists(settingsPath))
                return;

            string content = File.ReadAllText(settingsPath);
            const string key = "environment.visualExperience.colorTheme";
            string pattern = "\"" + Regex.Escape(key) + "\"\\s*:\\s*\"[^\"]*\"";
            string replacement = "\"" + key + "\": \"" + themeSlug + "\"";

            if (Regex.IsMatch(content, pattern))
            {
                content = Regex.Replace(content, pattern, replacement);
            }
            else
            {
                // Insert before the closing brace
                int lastBrace = content.LastIndexOf('}');
                if (lastBrace < 0)
                    return;
                content = content.Substring(0, lastBrace).TrimEnd()
                    + ",\n  " + replacement + "\n}";
            }

            File.WriteAllText(settingsPath, content);

            ClearFontAndColorCaches();
        }

        private void ClearFontAndColorCaches()
        {
            ThreadHelper.ThrowIfNotOnUIThread();

            var cacheManager = GetService(typeof(SVsFontAndColorCacheManager)) as IVsFontAndColorCacheManager;
            if (cacheManager != null)
            {
                cacheManager.ClearAllCaches();
            }

            var storage = GetService(typeof(SVsFontAndColorStorage)) as IVsFontAndColorStorage;
            if (storage != null)
            {
                // Text Editor category
                var textEditorCategory = new Guid("{A27B4E24-A735-4d1d-B8E7-9716E1E3D8E0}");
                // Output Window category
                var outputWindowCategory = new Guid("{9973EFDF-317D-431C-8BC1-5E88CBFD4F7F}");

                // FCSF_LOADDEFAULTS (0x2) | FCSF_PROPAGATECHANGES (0x8)
                const uint flags = 0x2 | 0x8;

                var categories = new[] { textEditorCategory, outputWindowCategory };
                for (int i = 0; i < categories.Length; i++)
                {
                    var cat = categories[i];
                    if (storage.OpenCategory(ref cat, flags) == 0)
                    {
                        storage.CloseCategory();
                    }
                }
            }

            if (cacheManager != null)
            {
                cacheManager.ClearAllCaches();
            }
        }

        private string GetSettingsJsonPath()
        {
            ThreadHelper.ThrowIfNotOnUIThread();

            using (var regKey = UserRegistryRoot)
            {
                if (regKey == null)
                    return null;
                // regKey.Name = "HKEY_CURRENT_USER\Software\Microsoft\VisualStudio\18.0_b2d91ac9"
                string fullPath = regKey.Name;
                string instanceId = fullPath.Substring(fullPath.LastIndexOf('\\') + 1);
                return Path.Combine(
                    Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
                    "Microsoft", "VisualStudio", instanceId, "settings.json");
            }
        }
    }
}
