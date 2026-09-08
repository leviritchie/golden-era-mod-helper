// Teaching copy. Not compiled into any game plugin.
// Replace every LiveType_* / LiveMethod_* pin after you re-pin GameAssembly.

internal static class GameSymbols
{
	internal static class BattleUnitInit
	{
		internal const string UnitTypeId = "Hex.Session.Battle.Unit";
		internal static readonly string[] SideTypeHints =
		{
			"LiveType_UnitInitSideWrapper",
		};
		internal static readonly MethodSymbol Init = new("battle.unit.init", "Init");
	}

	internal static class FocusLaws
	{
		internal static readonly string[] AbilityConfigEnergyMembers =
		{
			"energyLevel",
			"dontUseEnergy",
			"cd",
			"sid",
			"id",
		};
	}

	internal readonly struct MethodSymbol
	{
		internal MethodSymbol(string id, string liveName)
		{
			Id = id;
			LiveName = liveName;
		}

		internal string Id { get; }
		internal string LiveName { get; }
	}
}
