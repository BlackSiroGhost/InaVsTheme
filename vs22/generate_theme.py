"""
Generate VS 2022 theme XML from One Dark Variant template + our color palette.
Context-aware: maps Background and Foreground elements differently.
"""
import re
import colorsys

VARIANTS = {
    "Ancient One Dark": {
        "guid": "{6e3a4f5b-8c2d-4a91-b7e0-1f9d3c5a2b80}",
        "shell_bg": (0x1D, 0x14, 0x2E),
        "editor_bg": (0x2B, 0x20, 0x3F),
        "surface": (0x33, 0x28, 0x48),       # slightly lighter than editor
        "hover": (0x3D, 0x31, 0x52),          # hover/selection bg
        "border": (0x50, 0x46, 0x62),         # borders
        "foreground": (0xC0, 0xBB, 0xCB),
        "fg_dim": (0x73, 0x68, 0x8D),         # comment/dim text
        "fg_mid": (0x99, 0x91, 0xAC),         # medium text
        "accent": (0xF4, 0xBA, 0x51),
        "accent_dark": (0xAD, 0x84, 0x39),    # darker accent
        "keyword": (0xC7, 0xA8, 0xED),
        "string": (0xE6, 0xBE, 0x7D),
        "number": (0xFC, 0x6A, 0x9D),
        "type": (0x5A, 0xA1, 0xDB),
        "method": (0xE6, 0x78, 0xE8),
    },
    "Ancient One Dark Violet": {
        "guid": "{7f4b5a6c-9d3e-4b02-c8f1-2a0e4d6b3c91}",
        "shell_bg": (0x19, 0x15, 0x2A),
        "editor_bg": (0x24, 0x1E, 0x3D),
        "surface": (0x2C, 0x26, 0x45),
        "hover": (0x36, 0x2F, 0x50),
        "border": (0x48, 0x40, 0x5E),
        "foreground": (0xBD, 0xB6, 0xCC),
        "fg_dim": (0x6B, 0x64, 0x90),
        "fg_mid": (0x94, 0x8D, 0xAE),
        "accent": (0xFD, 0xC9, 0x55),
        "accent_dark": (0xB3, 0x8E, 0x3C),
        "keyword": (0x80, 0x87, 0xEE),
        "string": (0xDD, 0xB6, 0x72),
        "number": (0xFF, 0x6B, 0x9D),
        "type": (0x75, 0xBC, 0xFF),
        "method": (0xFE, 0x71, 0x9E),
    },
    "Ancient One Dark Slate": {
        "guid": "{8a5c6b7d-0e4f-4c13-d902-3b1f5e7c4da2}",
        "shell_bg": (0x14, 0x14, 0x14),
        "editor_bg": (0x1C, 0x1C, 0x1D),
        "surface": (0x25, 0x25, 0x27),
        "hover": (0x30, 0x30, 0x33),
        "border": (0x44, 0x44, 0x48),
        "foreground": (0xB0, 0xAC, 0xB8),
        "fg_dim": (0x6A, 0x6A, 0x6A),
        "fg_mid": (0x8A, 0x8A, 0x8E),
        "accent": (0x6B, 0x71, 0xC4),
        "accent_dark": (0x4D, 0x52, 0x8E),
        "keyword": (0xBF, 0xBB, 0xCD),
        "string": (0xC9, 0xA9, 0x74),
        "number": (0xD4, 0x8E, 0x72),
        "type": (0x6E, 0xAC, 0xE5),
        "method": (0xC7, 0x76, 0xDD),
    },
}


# Environment Background elements that hold TEXT/GLYPH colors (should be light/readable).
# These get mangled by map_bg_color which treats bright whites as "light surfaces" → dark.
TEXT_AS_BG = {
    # File tabs
    "FileTabSelectedText": "foreground",
    "FileTabHotText": "foreground",
    "FileTabHotGlyph": "fg_mid",
    "FileTabInactiveText": "fg_mid",
    "FileTabText": "fg_mid",
    "FileTabLastActiveText": "fg_mid",
    "FileTabLastActiveGlyph": "fg_dim",
    "FileTabProvisionalSelectedActiveText": "foreground",
    "FileTabProvisionalInactiveText": "fg_mid",
    # Title bar
    "TitleBarActiveText": "foreground",
    "TitleBarInactiveText": "fg_dim",
    "TitleBarDragHandle": "fg_dim",
    # Status bar
    "StatusBarText": "foreground",
    # Tool windows
    "ToolWindowText": "foreground",
    "ToolWindowTabSelectedText": "foreground",
    "ToolWindowTabSelectedActiveText": "foreground",
    "ToolWindowTabText": "fg_mid",
    "ToolWindowTabMouseOverText": "foreground",
    "ToolWindowButtonActiveGlyph": "foreground",
    "ToolWindowButtonHoverActiveGlyph": "foreground",
    "ToolWindowButtonDownActiveGlyph": "foreground",
    "ToolWindowButtonInactiveGlyph": "fg_mid",
    "ToolWindowButtonHoverInactiveGlyph": "fg_mid",
    "ToolWindowButtonDownInactiveGlyph": "fg_mid",
    # Toolbar / command bar text
    "CommandBarTextActive": "foreground",
    "CommandBarTextHover": "foreground",
    "CommandBarTextInactive": "fg_dim",
    "CommandBarTextSelected": "foreground",
    "CommandBarTextMouseOverUnfocused": "foreground",
    # Panel title bar
    "PanelTitleBarText": "foreground",
    "PanelTitleBarTextUnfocused": "fg_dim",
    # Menu text
    "MenuText": "foreground",
    # Environment DropDown text/glyph tokens
    "DropDownText": "foreground",
    "DropDownDisabledText": "fg_dim",
    "DropDownMouseOverText": "foreground",
    "DropDownMouseDownText": "foreground",
    "DropDownGlyph": "fg_mid",
    "DropDownDisabledGlyph": "fg_dim",
    "DropDownMouseOverGlyph": "accent",
    "DropDownMouseDownGlyph": "foreground",
    # Environment ComboBox text/glyph tokens
    "ComboBoxText": "foreground",
    "ComboBoxDisabledText": "fg_dim",
    "ComboBoxMouseOverText": "foreground",
    "ComboBoxMouseDownText": "foreground",
    "ComboBoxGlyph": "fg_mid",
    "ComboBoxDisabledGlyph": "fg_dim",
    "ComboBoxMouseOverGlyph": "accent",
    "ComboBoxMouseDownGlyph": "foreground",
    # Environment ComboBox dropdown LIST item text (separate from ComboBoxText!)
    "ComboBoxItemText": "foreground",
    "ComboBoxItemMouseOverText": "foreground",
    "ComboBoxItemTextInactive": "fg_dim",
    "ComboBoxFocusedText": "foreground",
    "ComboBoxFocusedGlyph": "fg_mid",
    "CommandBarMenuSubmenuGlyphHover": "foreground",
    # Menu glyphs
    "CommandBarMenuSubmenuGlyph": "fg_mid",
    "CommandBarMenuMouseOverSubmenuGlyph": "accent",
    "CommandBarMenuGlyph": "fg_mid",
    "CommandBarMenuMouseOverGlyph": "accent",
    "CommandBarMenuMouseDownGlyph": "foreground",
    "CommandBarMenuScrollGlyph": "fg_mid",
    "CommandBarMenuWatermarkText": "fg_dim",
    "CommandBarMenuWatermarkLinkText": "accent_dark",
    "CommandBarMenuWatermarkTextHover": "fg_mid",
    "CommandBarMenuWatermarkLinkTextHover": "accent",
    "CommandBarMenuLinkText": "accent",
    "CommandBarMenuLinkTextHover": "foreground",
    "CommandBarMenuGroupHeaderLinkText": "accent",
    "CommandBarMenuGroupHeaderLinkTextHover": "foreground",
    # Search box
    "SearchBoxText": "foreground",
    "SearchBoxWatermarkText": "fg_dim",
    # Auto-hide tabs
    "AutoHideTabText": "fg_mid",
    "AutoHideTabMouseOverText": "foreground",
    # Toolbar option/overflow glyphs
    "CommandBarOptionsGlyph": "fg_mid",
    "CommandBarOptionsMouseOverGlyph": "foreground",
    "CommandBarOptionsMouseDownGlyph": "foreground",
    "CommandBarDragHandle": "fg_dim",
    # Scrollbar arrow glyphs
    "ScrollBarArrowGlyph": "fg_dim",
    "ScrollBarArrowGlyphMouseOver": "fg_mid",
    "ScrollBarArrowGlyphPressed": "foreground",
    "ScrollBarArrowGlyphDisabled": "fg_dim",
    # Main window button glyphs (min/max/close)
    "MainWindowButtonActiveGlyph": "foreground",
    "MainWindowButtonInactiveGlyph": "fg_dim",
    "MainWindowButtonHoverActiveGlyph": "foreground",
    "MainWindowButtonHoverInactiveGlyph": "fg_mid",
    "MainWindowButtonDownGlyph": "foreground",
}

# Environment Background elements — surface/chrome colors
BG_OVERRIDES = {
    # Active document tab
    "FileTabSelectedGradientTop": "editor_bg",
    "FileTabSelectedGradientMiddle1": "editor_bg",
    "FileTabSelectedGradientMiddle2": "editor_bg",
    "FileTabSelectedGradientBottom": "editor_bg",
    "FileTabSelectedBorder": "editor_bg",
    "FileTabSelectedBackground": "editor_bg",
    "FileTabDocumentBorderBackground": "editor_bg",
    "FileTabDocumentBorderShadow": "border",
    "FileTabDocumentBorderHighlight": "border",
    # Hover tab
    "FileTabHotGradientTop": "hover",
    "FileTabHotGradientBottom": "hover",
    "FileTabHotBorder": "hover",
    # Last active tab
    "FileTabLastActiveGradientTop": "surface",
    "FileTabLastActiveGradientMiddle1": "surface",
    "FileTabLastActiveGradientMiddle2": "surface",
    "FileTabLastActiveGradientBottom": "surface",
    "FileTabLastActiveDocumentBorderBackground": "surface",
    "FileTabLastActiveDocumentBorderEdge": "border",
    # Provisional tab (preview)
    "FileTabProvisionalSelectedActive": "accent_dark",
    "FileTabProvisionalSelectedActiveBorder": "accent_dark",
    "FileTabProvisionalHover": "accent_dark",
    "FileTabProvisionalHoverBorder": "accent_dark",
    # Inactive tabs + channel
    "FileTabInactiveGradientTop": "shell_bg",
    "FileTabInactiveGradientBottom": "shell_bg",
    "FileTabInactiveBorder": "shell_bg",
    "FileTabChannelBackground": "shell_bg",
    # Tool window tabs
    "ToolWindowTabSelectedTab": "editor_bg",
    "ToolWindowTabSelectedBorder": "editor_bg",
    "ToolWindowTabMouseOverBackgroundBegin": "hover",
    "ToolWindowTabMouseOverBackgroundEnd": "hover",
    "ToolWindowTabMouseOverBorder": "hover",
    "ToolWindowTabGradientBegin": "shell_bg",
    "ToolWindowTabGradientEnd": "shell_bg",
    "ToolWindowTabBorder": "shell_bg",
    # Tool window content
    "ToolWindowBackground": "editor_bg",
    "ToolWindowBorder": "border",
    "ToolWindowContentGrid": "editor_bg",
    "ToolWindowContentTabGradientBegin": "editor_bg",
    "ToolWindowContentTabGradientEnd": "editor_bg",
    # Panel title bar
    "PanelTitleBar": "surface",
    "PanelTitleBarUnfocused": "shell_bg",
    # Environment DropDown surfaces
    "DropDownBackground": "surface",
    "DropDownBorder": "border",
    "DropDownMouseDownBackground": "surface",
    "DropDownMouseDownBorder": "border",
    "DropDownMouseOverBackgroundBegin": "hover",
    "DropDownMouseOverBackgroundMiddle1": "hover",
    "DropDownMouseOverBackgroundMiddle2": "hover",
    "DropDownMouseOverBackgroundEnd": "hover",
    "DropDownMouseOverBorder": "border",
    "DropDownPopupBackgroundBegin": "surface",
    "DropDownPopupBackgroundEnd": "surface",
    "DropDownPopupBorder": "border",
    "DropDownDisabledBackground": "shell_bg",
    "DropDownDisabledBorder": "shell_bg",
    "DropDownButtonMouseOverBackground": "hover",
    "DropDownButtonMouseOverSeparator": "border",
    "DropDownButtonMouseDownBackground": "hover",
    "DropDownButtonMouseDownSeparator": "border",
    # Environment ComboBox surfaces
    "ComboBoxBackground": "surface",
    "ComboBoxBorder": "border",
    "ComboBoxDisabledBackground": "shell_bg",
    "ComboBoxDisabledBorder": "shell_bg",
    "ComboBoxMouseDownBackground": "surface",
    "ComboBoxMouseDownBorder": "accent_dark",
    "ComboBoxMouseOverBackgroundBegin": "hover",
    "ComboBoxMouseOverBackgroundMiddle1": "hover",
    "ComboBoxMouseOverBackgroundMiddle2": "hover",
    "ComboBoxMouseOverBackgroundEnd": "hover",
    "ComboBoxMouseOverBorder": "border",
    "ComboBoxPopupBackgroundBegin": "surface",
    "ComboBoxPopupBackgroundEnd": "surface",
    "ComboBoxPopupBorder": "border",
    "ComboBoxSelection": "accent_dark",
    "ComboBoxButtonMouseOverBackground": "hover",
    "ComboBoxButtonMouseOverSeparator": "border",
    "ComboBoxButtonMouseDownBackground": "accent_dark",
    "ComboBoxButtonMouseDownSeparator": "accent_dark",
    "ComboBoxFocusedButtonSeparator": "accent_dark",
    "ComboBoxFocusedBackground": "surface",
    "ComboBoxFocusedBorder": "border",
    "ComboBoxFocusedButtonBackground": "surface",
    "ComboBoxItemMouseOverBackground": "hover",
    "ComboBoxItemMouseOverBorder": "hover",
    "ComboBoxFocusBox": "surface",
    # Title bar
    "TitleBarActive": "shell_bg",
    "TitleBarInactive": "shell_bg",
    # Menu bar / command bar backgrounds
    "Menu": "shell_bg",
    "CommandBarGradientBegin": "shell_bg",
    "CommandBarGradientMiddle": "shell_bg",
    "CommandBarGradientEnd": "shell_bg",
    "CommandBarToolBarBorder": "shell_bg",
    "CommandBarToolBarSeparator": "border",
    "CommandBarToolBarSeparatorHighlight": "border",
    # Menu dropdown backgrounds
    "CommandBarMenuBackgroundGradientBegin": "surface",
    "CommandBarMenuBackgroundGradientEnd": "surface",
    "CommandBarMenuBorder": "border",
    "CommandBarMenuIconBackground": "surface",
    "CommandBarMenuItemMouseOver": "hover",
    "CommandBarMenuItemMouseOverBorder": "hover",
    "CommandBarMenuSeparator": "border",
    "CommandBarMenuMouseOverSeparator": "hover",
    # Toolbar buttons hover/press
    "CommandBarMouseOverBackgroundBegin": "hover",
    "CommandBarMouseOverBackgroundMiddle1": "hover",
    "CommandBarMouseOverBackgroundMiddle2": "hover",
    "CommandBarMouseOverBackgroundEnd": "hover",
    "CommandBarMouseDownBackgroundBegin": "surface",
    "CommandBarMouseDownBackgroundMiddle": "surface",
    "CommandBarMouseDownBackgroundEnd": "surface",
    # Toolbar overflow
    "CommandBarOptionsBackground": "surface",
    "CommandBarOptionsMouseOverBackgroundBegin": "hover",
    "CommandBarOptionsMouseOverBackgroundEnd": "hover",
    "CommandBarOptionsMouseDownBackgroundBegin": "surface",
    "CommandBarOptionsMouseDownBackgroundEnd": "surface",
    "CommandBarDragHandleShadow": "shell_bg",
    # Search box
    "SearchBoxBackground": "surface",
    "SearchBoxBorder": "border",
    # Status bar
    "StatusBarDefault": "shell_bg",
    "StatusBarHighlight": "hover",
    # Scrollbars
    "ScrollBarBackground": "shell_bg",
    "ScrollBarThumbBackground": "border",
    "ScrollBarThumbMouseOverBackground": "fg_dim",
    "ScrollBarThumbPressedBackground": "fg_mid",
    "ScrollBarArrowBackground": "shell_bg",
    "ScrollBarArrowMouseOverBackground": "hover",
    "ScrollBarArrowPressedBackground": "surface",
    # Auto-hide tabs
    "AutoHideTabBackgroundBegin": "shell_bg",
    "AutoHideTabBackgroundEnd": "shell_bg",
    "AutoHideTabBorder": "shell_bg",
    "AutoHideTabMouseOverBackgroundBegin": "hover",
    "AutoHideTabMouseOverBackgroundEnd": "hover",
    "AutoHideTabMouseOverBorder": "hover",
    # Grippers
    "GripperHorizontalBackground": "shell_bg",
    "GripperVerticalBackground": "shell_bg",
    # Main window buttons (min/max/close)
    "MainWindowButtonActive": "shell_bg",
    "MainWindowButtonInactive": "shell_bg",
    "MainWindowButtonHoverActive": "hover",
    "MainWindowButtonHoverInactive": "hover",
    "MainWindowButtonDown": "surface",
    "MainWindowButtonDownBorder": "accent_dark",
    # Document well
    "DocumentWellOverflowButtonBackground": "shell_bg",
    "DocumentWellOverflowButtonGlyph": "fg_mid",
    "DocumentWellOverflowButtonMouseOverBackground": "hover",
    "DocumentWellOverflowButtonMouseOverGlyph": "foreground",
    "DocumentWellOverflowButtonMouseDownBackground": "surface",
    "DocumentWellOverflowButtonMouseDownGlyph": "foreground",
    # Splitter / resize handle
    "EnvironmentBackground": "shell_bg",
    "SplitterBackground": "shell_bg",
}


# Overrides for "Text Editor Text Marker Items" — debug highlights, breakpoints
# VS 2026 doesn't define these; it uses VS defaults. Template has bright yellows.
MARKER_OVERRIDES = {
    "Current Statement": {"bg": "hover", "fg": "foreground"},
    "Executing Thread IP": {"bg": "surface", "fg": "foreground"},
    "Call Return": {"bg": "surface", "fg": "foreground"},
    "Call Return (historical mode)": {"bg": "surface", "fg": "fg_mid"},
    "Current Statement (historical mode)": {"bg": "surface", "fg": "fg_mid"},
    "Coverage Touched Area": {"bg": "surface", "fg": "foreground"},
    "Coverage Not Touched Area": {"bg": "editor_bg", "fg": "fg_mid"},
    "Coverage Partially Touched Area": {"bg": "surface", "fg": "foreground"},
}

# Overrides for "ColorizedSignatureHelp colors" — outlining, highlights
SIGHELP_OVERRIDES = {
    "outlining.square": {"bg": "surface", "fg": "fg_dim"},
    "outlining.collapsehintadornment": {"bg": "surface", "fg": "foreground"},
    "HTML Server-Side Script": {"bg": "surface", "fg": "fg_mid"},
}

# TreeView (Solution Explorer, etc.)
TREEVIEW_OVERRIDES = {
    "Background": {"bg": "editor_bg"},
    "SelectedItemActive": {"bg": "hover", "fg": "foreground"},
    "SelectedItemInactive": {"bg": "surface", "fg": "fg_mid"},
    "Glyph": {"fg": "fg_mid"},
    "GlyphMouseOver": {"fg": "foreground"},
    "SelectedItemActiveGlyph": {"fg": "foreground"},
    "SelectedItemActiveGlyphMouseOver": {"fg": "foreground"},
    "SelectedItemInactiveGlyph": {"fg": "fg_mid"},
    "SelectedItemInactiveGlyphMouseOver": {"fg": "fg_mid"},
    "DragOverItem": {"bg": "hover"},
    "FocusVisualBorder": {"bg": "accent_dark"},
    "HighlightedSpan": {"bg": "hover"},
}

# Output Window
OUTPUT_WINDOW_OVERRIDES = {
    "Plain Text": {"bg": "editor_bg", "fg": "foreground"},
    "Selected Text": {"bg": "hover"},
    "Inactive Selected Text": {"bg": "surface"},
    "urlformat": {"bg": "editor_bg", "fg": "accent"},
    "OutputHeading": {"fg": "accent"},
    "OutputVerbose": {"fg": "fg_mid"},
}

# Overrides for other categories with dark-FG-on-dark-BG issues
INFOBAR_OVERRIDES = {
    "Button": {"fg": "foreground"},
    "ButtonMouseOver": {"fg": "foreground"},
    "ButtonFocus": {"fg": "foreground"},
}

# CommonControls — all tokens use <Background> only, some also have <Foreground>
COMMONCONTROLS_OVERRIDES = {
    # Buttons (template uses "Button" with BG+FG, not separate "ButtonText"/"ButtonBackground")
    "Button": {"bg": "surface", "fg": "foreground"},
    "ButtonDefault": {"bg": "surface", "fg": "foreground"},
    "ButtonHover": {"bg": "hover", "fg": "foreground"},
    "ButtonPressed": {"bg": "accent_dark", "fg": "foreground"},
    "ButtonFocused": {"bg": "surface", "fg": "foreground"},
    "ButtonDisabled": {"bg": "shell_bg", "fg": "fg_dim"},
    "ButtonBorder": {"bg": "border"},
    "ButtonBorderDefault": {"bg": "accent_dark"},
    "ButtonBorderHover": {"bg": "accent"},
    "ButtonBorderPressed": {"bg": "accent_dark"},
    "ButtonBorderFocused": {"bg": "accent"},
    "ButtonBorderDisabled": {"bg": "border"},
    "FocusVisual": {"bg": "surface", "fg": "foreground"},
    # CheckBox text (Background-only tokens)
    "CheckBoxText": {"bg": "foreground"},
    "CheckBoxTextHover": {"bg": "foreground"},
    "CheckBoxTextPressed": {"bg": "foreground"},
    "CheckBoxTextFocused": {"bg": "foreground"},
    "CheckBoxTextDisabled": {"bg": "fg_dim"},
    "CheckBoxBackground": {"bg": "editor_bg"},
    "CheckBoxBackgroundHover": {"bg": "editor_bg"},
    "CheckBoxBackgroundPressed": {"bg": "accent_dark"},
    "CheckBoxBackgroundFocused": {"bg": "editor_bg"},
    "CheckBoxBackgroundDisabled": {"bg": "shell_bg"},
    "CheckBoxBorder": {"bg": "fg_dim"},
    "CheckBoxBorderHover": {"bg": "accent"},
    "CheckBoxBorderPressed": {"bg": "accent_dark"},
    "CheckBoxBorderFocused": {"bg": "accent"},
    "CheckBoxBorderDisabled": {"bg": "border"},
    "CheckBoxGlyph": {"bg": "foreground"},
    "CheckBoxGlyphHover": {"bg": "foreground"},
    "CheckBoxGlyphPressed": {"bg": "foreground"},
    "CheckBoxGlyphFocused": {"bg": "foreground"},
    "CheckBoxGlyphDisabled": {"bg": "fg_dim"},
    # ComboBox
    "ComboBoxText": {"bg": "foreground"},
    "ComboBoxTextHover": {"bg": "foreground"},
    "ComboBoxTextPressed": {"bg": "foreground"},
    "ComboBoxTextFocused": {"bg": "foreground"},
    "ComboBoxTextDisabled": {"bg": "fg_dim"},
    "ComboBoxTextInputSelection": {"bg": "hover"},
    "ComboBoxBackground": {"bg": "surface"},
    "ComboBoxBackgroundHover": {"bg": "hover"},
    "ComboBoxBackgroundPressed": {"bg": "surface"},
    "ComboBoxBackgroundFocused": {"bg": "surface"},
    "ComboBoxBackgroundDisabled": {"bg": "shell_bg"},
    "ComboBoxBorder": {"bg": "border"},
    "ComboBoxBorderHover": {"bg": "accent"},
    "ComboBoxBorderPressed": {"bg": "accent_dark"},
    "ComboBoxBorderFocused": {"bg": "accent_dark"},
    "ComboBoxBorderDisabled": {"bg": "border"},
    "ComboBoxGlyph": {"bg": "fg_mid"},
    "ComboBoxGlyphHover": {"bg": "accent"},
    "ComboBoxGlyphPressed": {"bg": "foreground"},
    "ComboBoxGlyphFocused": {"bg": "foreground"},
    "ComboBoxGlyphDisabled": {"bg": "fg_dim"},
    "ComboBoxGlyphBackground": {"bg": "surface"},
    "ComboBoxGlyphBackgroundHover": {"bg": "hover"},
    "ComboBoxGlyphBackgroundPressed": {"bg": "accent_dark"},
    "ComboBoxGlyphBackgroundFocused": {"bg": "surface"},
    "ComboBoxGlyphBackgroundDisabled": {"bg": "shell_bg"},
    "ComboBoxSeparator": {"bg": "border"},
    "ComboBoxSeparatorHover": {"bg": "accent"},
    "ComboBoxSeparatorPressed": {"bg": "accent_dark"},
    "ComboBoxSeparatorFocused": {"bg": "accent_dark"},
    "ComboBoxSeparatorDisabled": {"bg": "border"},
    "ComboBoxListBackground": {"bg": "surface"},
    "ComboBoxListBorder": {"bg": "border"},
    "ComboBoxListItemText": {"bg": "foreground"},
    "ComboBoxListItemTextHover": {"bg": "foreground"},
    "ComboBoxListItemBackgroundHover": {"bg": "hover"},
    "ComboBoxListItemBorderHover": {"bg": "hover"},
    "ComboBoxSelection": {"bg": "accent_dark"},
    # TextBox
    "TextBoxText": {"bg": "foreground"},
    "TextBoxTextDisabled": {"bg": "fg_dim"},
    "TextBoxTextFocused": {"bg": "foreground"},
    "TextBoxBackground": {"bg": "surface"},
    "TextBoxBackgroundDisabled": {"bg": "shell_bg"},
    "TextBoxBackgroundFocused": {"bg": "surface"},
    "TextBoxBorder": {"bg": "border"},
    "TextBoxBorderDisabled": {"bg": "border"},
    "TextBoxBorderFocused": {"bg": "accent_dark"},
    # Inner tabs (used in some tool windows)
    "InnerTabActiveBackground": {"bg": "editor_bg"},
    "InnerTabActiveBorder": {"bg": "accent_dark"},
    "InnerTabActiveText": {"bg": "foreground"},
    "InnerTabInactiveBackground": {"bg": "shell_bg"},
    "InnerTabInactiveBorder": {"bg": "shell_bg"},
    "InnerTabInactiveText": {"bg": "fg_mid"},
    "InnerTabInactiveHoverBackground": {"bg": "hover"},
    "InnerTabInactiveHoverBorder": {"bg": "hover"},
    "InnerTabInactiveHoverText": {"bg": "foreground"},
}

# Text Editor categories — tokens to preserve from the template (not in VS 2026)
# These get remapped by bulk color mapping but are lost when VS 2026 replaces the category
TEXT_EDITOR_EXTRA_OVERRIDES = {
    "outlining.collapsehintadornment": {"bg": "surface", "fg": "foreground"},
    "outlining.square": {"bg": "editor_bg", "fg": "fg_dim"},
    "Indicator Margin": {"bg": "surface"},
    "Selected Text": {"bg": "hover"},
    "Inactive Selected Text": {"bg": "surface"},
    "Visible Whitespace": {"fg": "border"},
}


def lum(r, g, b):
    return 0.299 * r + 0.587 * g + 0.114 * b


def clamp(v):
    return max(0, min(255, int(round(v))))


def lerp(c1, c2, t):
    return tuple(clamp(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


def is_saturated(r, g, b):
    mx, mn = max(r, g, b), min(r, g, b)
    return (mx - mn) / max(mx, 1) > 0.25


def hue_deg(r, g, b):
    h, _, _ = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
    return h * 360


def map_bg_color(hex_argb, p):
    """Map a Background color value."""
    a = int(hex_argb[0:2], 16)
    r, g, b = int(hex_argb[2:4], 16), int(hex_argb[4:6], 16), int(hex_argb[6:8], 16)

    if a == 0:
        return hex_argb

    L = lum(r, g, b)

    # Saturated backgrounds: blues/purples → purple tints, NOT gold
    if is_saturated(r, g, b):
        h = hue_deg(r, g, b)
        _, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
        # Blues/indigos/purples (180-300) → our purple palette tints
        if 180 <= h <= 300:
            if v < 0.35:
                nr, ng, nb = p["shell_bg"]
            elif v < 0.55:
                nr, ng, nb = p["surface"]
            elif v < 0.75:
                nr, ng, nb = p["hover"]
            else:
                nr, ng, nb = p["border"]
            return f"{a:02X}{clamp(nr):02X}{clamp(ng):02X}{clamp(nb):02X}"
        # Reds, greens, yellows/oranges → keep for status indicators
        return hex_argb

    # Neutral backgrounds: map by luminance to our dark palette
    if L < 15:
        nr, ng, nb = lerp(p["shell_bg"], (0, 0, 0), 0.4)
    elif L < 32:
        nr, ng, nb = p["shell_bg"]
    elif L < 50:
        nr, ng, nb = lerp(p["shell_bg"], p["editor_bg"], 0.6)
    elif L < 70:
        nr, ng, nb = p["editor_bg"]
    elif L < 90:
        nr, ng, nb = p["surface"]
    elif L < 120:
        nr, ng, nb = p["hover"]
    elif L < 160:
        nr, ng, nb = p["border"]
    elif L < 200:
        nr, ng, nb = p["surface"]
    elif L < 240:
        nr, ng, nb = p["editor_bg"]
    else:
        nr, ng, nb = p["surface"]

    return f"{a:02X}{clamp(nr):02X}{clamp(ng):02X}{clamp(nb):02X}"


def map_fg_color(hex_argb, p):
    """Map a Foreground color value."""
    a = int(hex_argb[0:2], 16)
    r, g, b = int(hex_argb[2:4], 16), int(hex_argb[4:6], 16), int(hex_argb[6:8], 16)

    if a == 0:
        return hex_argb

    L = lum(r, g, b)

    # Saturated foregrounds: blues/purples → accent gold (for links, highlights)
    if is_saturated(r, g, b):
        h = hue_deg(r, g, b)
        _, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
        if 180 <= h <= 300:
            # Bright blues → accent, dim blues → accent_dark
            if v > 0.6:
                nr, ng, nb = p["accent"]
            else:
                nr, ng, nb = p["accent_dark"]
            return f"{a:02X}{nr:02X}{ng:02X}{nb:02X}"
        # Reds, greens, yellows → keep as-is (status text)
        return hex_argb

    # Neutral foregrounds: map by luminance (inverted for dark theme)
    # Dark neutrals (#000000, #1E1E1E) were black text on light surfaces.
    # Since all surfaces are now dark, invert dark text → light text.
    if L < 30:
        nr, ng, nb = p["foreground"]
    elif L < 60:
        nr, ng, nb = p["fg_mid"]
    elif L < 100:
        nr, ng, nb = p["fg_dim"]
    elif L < 160:
        nr, ng, nb = p["fg_mid"]
    else:
        nr, ng, nb = p["foreground"]

    return f"{a:02X}{clamp(nr):02X}{clamp(ng):02X}{clamp(nb):02X}"


# Patterns in token names that indicate Background holds a TEXT/GLYPH color
_TEXT_BG_PATTERNS = re.compile(
    r'(?:Text|Glyph|Caption|Label|Title|Link|Letter|DragHandle|Arrow|Heading|'
    r'Separator|Handle|Chevron|Checkmark|SubmenuGlyph|ScrollGlyph|Watermark)',
    re.IGNORECASE
)

# Patterns that are NOT text even though they match above (actual surfaces/backgrounds)
_NOT_TEXT_PATTERNS = re.compile(
    r'(?:Background|Border|Fill|Gradient|Shadow|Texture|Begin|End|Middle|Shelf|'
    r'Highlight$|Stroke|Arrow(?:Background)|GlyphBackground)',
    re.IGNORECASE
)


def is_text_as_bg_token(token_name):
    """Detect if a token stores text/glyph color in its Background element.

    In VS themes, many tokens use Background-only to store text colors.
    Token names like "ComboBoxText", "MenuGlyph", "TabItemCaption" are text.
    Token names like "ComboBoxBackground", "GradientBegin" are actual surfaces.
    """
    if _NOT_TEXT_PATTERNS.search(token_name):
        return False
    if _TEXT_BG_PATTERNS.search(token_name):
        return True
    return False


def remap_color_element(block, palette):
    """Remap a single <Color>...</Color> block with context-aware mapping."""
    # Extract token name for context
    name_m = re.match(r'<Color Name="([^"]*)"', block)
    token_name = name_m.group(1) if name_m else ""

    # Detect if this token's Background holds text (not a surface)
    has_fg = '<Foreground' in block
    bg_is_text = not has_fg and is_text_as_bg_token(token_name)

    def remap_bg(m):
        prefix = m.group(1)
        hex_val = m.group(2)
        suffix = m.group(3)
        if bg_is_text:
            return f'{prefix}{map_fg_color(hex_val, palette)}{suffix}'
        return f'{prefix}{map_bg_color(hex_val, palette)}{suffix}'

    def remap_fg(m):
        prefix = m.group(1)
        hex_val = m.group(2)
        suffix = m.group(3)
        return f'{prefix}{map_fg_color(hex_val, palette)}{suffix}'

    block = re.sub(
        r'(<Background[^>]*Source=")([A-Fa-f0-9]{8})(")',
        remap_bg, block
    )
    block = re.sub(
        r'(<Foreground[^>]*Source=")([A-Fa-f0-9]{8})(")',
        remap_fg, block
    )
    return block


def remap_theme_xml(template, palette, name, guid):
    """Remap all colors in a theme XML template."""
    result = re.sub(
        r'<Theme Name="[^"]*" GUID="[^"]*"',
        f'<Theme Name="{name}" GUID="{guid}"',
        template
    )

    # Remap each Color block individually
    result = re.sub(
        r'(<Color Name="[^"]*">.*?</Color>)',
        lambda m: remap_color_element(m.group(1), palette),
        result,
        flags=re.DOTALL
    )

    return result


def apply_category_overrides(theme_xml, category_name, overrides, palette):
    """Apply explicit color overrides to a specific category.
    overrides: dict of token_name -> {"bg": palette_key, "fg": palette_key} (either optional)
    """
    cat_match = re.search(
        rf'(<Category Name="{re.escape(category_name)}"[^>]*>)(.*?)(</Category>)',
        theme_xml, re.DOTALL
    )
    if not cat_match:
        return theme_xml

    body = cat_match.group(2)

    for token_name, color_spec in overrides.items():
        if isinstance(color_spec, str):
            color_spec = {"bg": color_spec}

        if "bg" in color_spec:
            r, g, b = palette[color_spec["bg"]]
            pattern = rf'(<Color Name="{re.escape(token_name)}">.*?<Background[^>]*Source=")([A-Fa-f0-9]{{8}})(".*?</Color>)'
            m = re.search(pattern, body, re.DOTALL)
            if m:
                alpha = m.group(2)[0:2]
                new_val = f"{alpha}{r:02X}{g:02X}{b:02X}"
                body = body[:m.start(2)] + new_val + body[m.end(2):]

        if "fg" in color_spec:
            r, g, b = palette[color_spec["fg"]]
            pattern = rf'(<Color Name="{re.escape(token_name)}">.*?<Foreground[^>]*Source=")([A-Fa-f0-9]{{8}})(".*?</Color>)'
            m = re.search(pattern, body, re.DOTALL)
            if m:
                alpha = m.group(2)[0:2]
                new_val = f"{alpha}{r:02X}{g:02X}{b:02X}"
                body = body[:m.start(2)] + new_val + body[m.end(2):]

    return theme_xml[:cat_match.start(2)] + body + theme_xml[cat_match.end(2):]


def extract_category_tokens(vstheme_path, theme_name, category_prefix):
    """Extract individual tokens from categories matching prefix in a theme file."""
    with open(vstheme_path, 'r', encoding='utf-8') as f:
        content = f.read()

    pattern = rf'<Theme Name="{re.escape(theme_name)}".*?</Theme>'
    m = re.search(pattern, content, re.DOTALL)
    if not m:
        return {}

    # Returns {category_name: {token_name: token_xml, ...}, ...}
    result = {}
    for cat_m in re.finditer(
        rf'(<Category Name="({re.escape(category_prefix)}[^"]*)"[^>]*>)(.*?)(</Category>)',
        m.group(0), re.DOTALL
    ):
        cat_name = cat_m.group(2)
        cat_header = cat_m.group(1)
        cat_body = cat_m.group(3)
        tokens = {}
        for tok_m in re.finditer(
            r'(<Color Name="([^"]+)">.*?</Color>)',
            cat_body, re.DOTALL
        ):
            tokens[tok_m.group(2)] = tok_m.group(1)
        result[cat_name] = {"header": cat_header, "tokens": tokens}
    return result


def merge_text_editor_categories(theme_xml, vs26_cats):
    """Merge VS 2026 syntax tokens INTO existing template categories.

    For each Text Editor category that exists in both:
    - VS 2026 tokens replace template tokens (exact syntax colors)
    - Template tokens NOT in VS 2026 are preserved (outlining, margins, etc.)

    VS 2026 categories not in template are appended.
    """
    for cat_name, cat_data in vs26_cats.items():
        cat_pattern = rf'(<Category Name="{re.escape(cat_name)}"[^>]*>)(.*?)(</Category>)'
        cat_match = re.search(cat_pattern, theme_xml, re.DOTALL)

        if cat_match:
            # Category exists in template — merge tokens
            tmpl_body = cat_match.group(2)

            for token_name, token_xml in cat_data["tokens"].items():
                tok_pattern = rf'<Color Name="{re.escape(token_name)}">.*?</Color>'
                if re.search(tok_pattern, tmpl_body, re.DOTALL):
                    # Replace existing token
                    tmpl_body = re.sub(tok_pattern, token_xml.strip(), tmpl_body, flags=re.DOTALL)
                else:
                    # Append new token (VS 2026 has it, template doesn't)
                    tmpl_body += f"\n            {token_xml.strip()}"

            theme_xml = (theme_xml[:cat_match.start(2)] + tmpl_body +
                        theme_xml[cat_match.end(2):])
        else:
            # Category doesn't exist in template — append entire category
            full_cat = cat_data["header"]
            for token_xml in cat_data["tokens"].values():
                full_cat += f"\n            {token_xml.strip()}"
            full_cat += "\n        </Category>"
            theme_xml = theme_xml.replace('</Theme>', f'\t\t{full_cat}\n\t</Theme>')

    return theme_xml


def build_vs22_theme():
    with open('C:/Users/Ghost-PC/AppData/Local/Temp/VS-ColorThemes/VSColorThemes/Themes/OneDarkVariant.xml', 'r') as f:
        template = f.read()

    theme_match = re.search(r'(<Theme .*?</Theme>)', template, re.DOTALL)
    theme_template = theme_match.group(1)

    vs26_path = 'C:/Users/Ghost-PC/Projects/InaVsTheme/src/AncientOneDark.vstheme'

    output_themes = []
    for name, palette in VARIANTS.items():
        print(f"Generating {name}...")
        remapped = remap_theme_xml(theme_template, palette, name, palette["guid"])

        # Fix Environment tokens that bulk remapping gets wrong
        env_overrides = {}
        for token, key in TEXT_AS_BG.items():
            env_overrides[token] = {"bg": key}
        for token, key in BG_OVERRIDES.items():
            env_overrides[token] = {"bg": key}
        remapped = apply_category_overrides(remapped, "Environment", env_overrides, palette)

        # Fix debug highlight markers (bright yellows → muted palette colors)
        remapped = apply_category_overrides(remapped, "Text Editor Text Marker Items", MARKER_OVERRIDES, palette)

        # Fix outlining/collapse indicators
        remapped = apply_category_overrides(remapped, "ColorizedSignatureHelp colors", SIGHELP_OVERRIDES, palette)

        # Fix InfoBar button text
        remapped = apply_category_overrides(remapped, "InfoBar", INFOBAR_OVERRIDES, palette)

        # Fix CommonControls (ComboBox, Button, TextBox, CheckBox readability)
        remapped = apply_category_overrides(remapped, "CommonControls", COMMONCONTROLS_OVERRIDES, palette)

        # Fix TreeView (Solution Explorer)
        remapped = apply_category_overrides(remapped, "TreeView", TREEVIEW_OVERRIDES, palette)

        # Fix Output Window
        remapped = apply_category_overrides(remapped, "Output Window", OUTPUT_WINDOW_OVERRIDES, palette)

        # Merge VS 2026 Text Editor syntax tokens (preserves template tokens like outlining)
        vs26_cats = extract_category_tokens(vs26_path, name, "Text Editor")
        remapped = merge_text_editor_categories(remapped, vs26_cats)

        # Apply Text Editor overrides for outlining, margins, selection (post-merge)
        for te_cat in ["Text Editor Text Manager Items", "Text Editor Language Service Items",
                       "Text Editor MEF Items", "ColorizedSignatureHelp colors"]:
            remapped = apply_category_overrides(remapped, te_cat, TEXT_EDITOR_EXTRA_OVERRIDES, palette)

        output_themes.append(remapped)

    output = '<Themes>\n\n'
    for theme in output_themes:
        output += theme + '\n\n'
    output += '</Themes>\n'

    out_path = 'C:/Users/Ghost-PC/Projects/InaVsTheme/vs22/AncientOneDark.vstheme'
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(output)

    print(f"\nWritten to {out_path}")

    # Verify
    for name, palette in VARIANTS.items():
        pattern = rf'<Theme Name="{re.escape(name)}".*?</Theme>'
        m = re.search(pattern, output, re.DOTALL)
        if m:
            env = re.search(r'<Category Name="Environment"[^>]*>(.*?)</Category>', m.group(0), re.DOTALL)
            env_count = len(re.findall(r'<Color Name=', env.group(1))) if env else 0
            total = len(re.findall(r'<Color Name=', m.group(0)))
            # Count bright backgrounds in Environment
            bright = 0
            if env:
                for bg_m in re.finditer(r'<Background[^>]*Source="([A-Fa-f0-9]{8})"', env.group(1)):
                    h = bg_m.group(1)
                    aa, rr, gg, bb = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16), int(h[6:8],16)
                    if aa > 100 and lum(rr, gg, bb) > 150:
                        bright += 1
            print(f"  {name}: {total} tokens, {env_count} env, {bright} bright env BGs")


if __name__ == '__main__':
    build_vs22_theme()
