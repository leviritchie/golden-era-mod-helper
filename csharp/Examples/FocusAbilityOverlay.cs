// Teaching copy. Not compiled into any game plugin.
// Overlay custom Focus icons. Do not write native viewBase.pics on the release path.

internal static class FocusAbilityOverlay
{
	internal const string OverlayChildName = "HOMM3_BATTLE_ABILITY_ICON";

	internal static void Bind(object abilityView, string unitSid, string iconKey, bool isCustom, Action<string> applyOverlay, Action clearOverlay, Action<int, int> refreshFocusPips, int focusCost)
	{
		if (!isCustom)
		{
			clearOverlay();
			return;
		}

		if (string.IsNullOrEmpty(iconKey) || iconKey.EndsWith("_name") || iconKey.Contains("@"))
			throw new System.InvalidOperationException("iconKey is not a runtime sprite key: " + iconKey);

		applyOverlay(iconKey);
		refreshFocusPips(focusCost, focusCost);
		// Keep native energyContainer above the overlay so Focus pips stay visible.
	}
}
