// Teaching copy. Not compiled into any game plugin.

using HarmonyLib;
using System;

internal static class FailClosedPatch
{
	internal static bool TryRegister(Harmony harmony, Action<string> log)
	{
		var method = AccessTools.Method(Type.GetType("LiveType_SelectedUnitHud"), "LiveMethod_Hotkey");
		if (method == null)
		{
			log("custom focus hotkeys skipped: live HotkeyAbilityArgs handler not found");
			return false;
		}

		harmony.Patch(method, postfix: new HarmonyMethod(typeof(FailClosedPatch), nameof(Postfix)));
		log("custom focus hotkeys REGISTERED_EXACT_POSTFIX");
		return true;
	}

	private static void Postfix(object __instance, object __0)
	{
		// Bind only when the current unit SID is yours.
		// Do not Input.GetKeyDown as a second owner.
	}
}
