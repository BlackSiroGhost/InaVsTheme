using System;
using System.ComponentModel.Design;
using System.IO;
using System.Runtime.InteropServices;
using System.Text.RegularExpressions;
using System.Threading;
using Microsoft.VisualStudio.Shell;
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

        // VS 2026 uses string slugs for theme identification
        private static readonly (int cmdId, string themeSlug)[] Themes = new[]
        {
            (CmdIdDark,       "ancient-one-dark"),
            (CmdIdDarkViolet, "ancient-one-dark-violet"),
            (CmdIdDarkSlate,  "ancient-one-dark-slate"),
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
