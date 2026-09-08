// Teaching copy. Not compiled into any game plugin.
// 1) Live arg type must match map key type (or bridge).
// 2) Then key Il2Cpp objects by native pointer, not managed GetHashCode.

using System;
using System.Collections.Generic;

internal static class NativePointerKeyedPlan
{
	private static readonly Dictionary<IntPtr, string> Plans = new Dictionary<IntPtr, string>();

	internal static void StoreFromUnitInit(object liveSideWrapper, string planId, Func<object, object> bridgeToTransferSide, Func<object, IntPtr> nativePointer)
	{
		var transferSide = bridgeToTransferSide(liveSideWrapper);
		if (transferSide == null)
			throw new InvalidOperationException("Unit.Init side wrapper did not bridge to TransferSide");

		var key = nativePointer(transferSide);
		if (key == IntPtr.Zero)
			throw new InvalidOperationException("native pointer for TransferSide was zero");

		Plans[key] = planId;
	}

	internal static bool TryApply(object liveSideWrapper, Func<object, object> bridgeToTransferSide, Func<object, IntPtr> nativePointer, out string planId)
	{
		planId = null;
		var transferSide = bridgeToTransferSide(liveSideWrapper);
		if (transferSide == null)
			return false;
		return Plans.TryGetValue(nativePointer(transferSide), out planId);
	}

	internal static void ClearAfterEveryConsumerRan()
	{
		Plans.Clear();
	}
}
