// Teaching copy. Not compiled into any game plugin.

using System;
using System.Collections.Generic;

internal static class DonorForwardLookup
{
	private static readonly Dictionary<string, string> CustomToDonor = new Dictionary<string, string>
	{
		{ "h3_example_pikeman", "esquire" },
	};

	internal static string DonorShellFor(string customSid)
	{
		if (!CustomToDonor.TryGetValue(customSid, out var donor))
			throw new InvalidOperationException("no donor shell for " + customSid);
		return donor;
	}

	internal static string CustomFromDonor(string donorSid, string exactContextSid)
	{
		if (string.IsNullOrEmpty(exactContextSid))
			throw new InvalidOperationException("refusing donor reverse lookup without exact context");

		// exactContextSid must be a saved original custom SID, live hire payload, or current city+join.
		// "a custom city was seen" is not context.
		if (CustomToDonor.TryGetValue(exactContextSid, out var mapped) && mapped == donorSid)
			return exactContextSid;

		throw new InvalidOperationException("ambiguous donor reverse lookup for " + donorSid);
	}
}
