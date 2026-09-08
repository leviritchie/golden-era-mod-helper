// Teaching copy. Not compiled into any game plugin.

internal static class OwnedTownWorld
{
	internal static bool IsPanelVisuallyOpen(bool canvasEnabled, float canvasGroupAlpha)
	{
		return canvasEnabled && canvasGroupAlpha > 0.01f;
	}

	internal static void OpenHallConstruction(bool upgradePanelVisuallyOpen, System.Action closeUpgrade, System.Action selectBuildingsConstruction)
	{
		if (upgradePanelVisuallyOpen)
			closeUpgrade();
		selectBuildingsConstruction();
	}

	internal static void RejectProductPaths(string paradigm)
	{
		if (paradigm != "owned_city_world")
			throw new System.InvalidOperationException("Route A posters and click relays are not the product town path");
	}
}
