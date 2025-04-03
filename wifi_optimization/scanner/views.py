from django.shortcuts import render
import subprocess
import speedtest
import os
import socket
import uuid
def suggest_best_channel(request):
    try:
        result = subprocess.run(
            ["/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport", "-s"],
            capture_output=True, text=True
        )
        lines = result.stdout.strip().split("\n")[1:]
        channels = {}

        for line in lines:
            parts = line.split()
            if len(parts) < 5:
                continue
            channel = parts[-4]
            channels[channel] = channels.get(channel, 0) + 1
        
        best_channel = min(channels, key=channels.get) if channels else "No Data"
    except Exception as e:
        best_channel = f"Error: {str(e)}"

    return render(request, 'scanner/best_channel.html', {"best_channel": best_channel})

def get_network_info(request):
    try:
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        mac_address = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(0, 2*6, 8)][::-1])
        network_info = {
            "hostname": hostname,
            "ip_address": ip_address,
            "mac_address": mac_address,
        }
    except Exception as e:
        network_info = {"error": str(e)}

    return render(request, 'scanner/network_info.html', {"network_info": network_info})


def ping_test(request):
    try:
        response = subprocess.run(["ping", "-c", "4", "8.8.8.8"], capture_output=True, text=True)
        output = response.stdout
    except Exception as e:
        output = f"Error: {str(e)}"
    
    return render(request, 'scanner/ping_test.html', {'ping_output': output})

def scan_wifi(request):
    try:
        result = subprocess.run(
            ["/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport", "-s"],
            capture_output=True, text=True
        )
        lines = result.stdout.strip().split("\n")[1:]
        networks = []

        for line in lines:
            parts = line.split()
            if len(parts) < 5:
                continue

            ssid = " ".join(parts[:-5])
            signal_strength = int(parts[-5])
            channel = parts[-4]
            frequency = parts[-3]
            security = parts[-1]

            networks.append({
                'ssid': ssid,
                'signal_strength': signal_strength,
                'channel': channel,
                'frequency': frequency,
                'security': security
            })

        networks.sort(key=lambda x: x['signal_strength'], reverse=True)
        return render(request,'scanner/signal.html',{'networks':networks})
    except Exception as e:
        h={"ssid": "Error", "signal_strength": "N/A", "channel": "N/A", "frequency": "N/A", "security": str(e)}
        return render(request,'scanner/signal.html',{'networks':h})
    
def get_speed_test(request):
    try:
        st=speedtest.Speedtest()
        upload=st.upload()
        download=st.download()
        speed={"download":download,"upload":upload}
        return render(request,'scanner/speed.html',{"speed":speed})
    except Exception as e:
        speed={"download":"N/A","upload":"N/A","error":str(e)}
        return render(request,'scanner/speed.html',{'speed':speed})
def dashboard(request):
    
    try:
        return render(request,'scanner/dashboard.html')
    except (BrokenPipeError, ConnectionResetError):
        pass  