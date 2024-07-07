def track_station_information(station, online_stations):
    status = "online" if station in online_stations else "offline"
    return {
            "coordination": station.position,
            "frequency": station.wintfs[0].freq,
            "mode": station.wintfs[0].mode,
            "tx_power": station.wintfs[0].txpower,
            "range": station.wintfs[0].range,
            "antenna_gain": station.wintfs[0].antennaGain,
            "status": status
    }
