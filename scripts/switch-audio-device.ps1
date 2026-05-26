# Switch default Windows playback device by friendly name pattern (requires device ID from caller)
param(
    [Parameter(Mandatory = $true)]
    [string]$DeviceId
)

$code = @"
using System;
using System.Runtime.InteropServices;

[ComImport, Guid("870AF99C-171D-4F9E-AF0D-E63DF40C2BC9")]
public class PolicyConfigClient { }

[Guid("F867B9F6-0A0C-4B7E-9C64-8F0E4B57A0C3")]
[InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
public interface IPolicyConfig {
    int Unused1();
    int Unused2();
    int Unused3();
    int Unused4();
    int Unused5();
    int Unused6();
    int Unused7();
    int Unused8();
    int Unused9();
    int Unused10();
    int SetDefaultEndpoint([MarshalAs(UnmanagedType.LPWStr)] string deviceId, int role);
}

public static class AudioSwitcher {
    public static int SetDefault(string id) {
        var policy = (IPolicyConfig)new PolicyConfigClient();
        return policy.SetDefaultEndpoint(id, 0);
    }
}
"@

Add-Type -TypeDefinition $code -Language CSharp
[AudioSwitcher]::SetDefault($DeviceId) | Out-Null
Write-Output "ok"
