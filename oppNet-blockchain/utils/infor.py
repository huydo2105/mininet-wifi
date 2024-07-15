def track_station_information(station, online_stations):
    status = "online" if station in online_stations else "offline"
    return {
        "position": ",".join(map(str, station.position)), 
        "frequency": str(station.wintfs[0].freq),
        "mode": station.wintfs[0].mode,
        "tx_power": str(station.wintfs[0].txpower),
        "range": str(station.wintfs[0].range),
        "antenna_gain": str(station.wintfs[0].antennaGain),
        "status": status
    }