import smartpy as sp

class NetworkInfoContract(sp.Contract):
    def __init__(self):
        self.init(
            timestamps={},
            latest_info={}
        )

    @sp.entry_point
    def store_network_info(self, params):
        timestamp = params.timestamp
        station_name = params.station_name

        # Update timestamps map
        if timestamp in self.data.timestamps:
            self.data.timestamps[timestamp][station_name] = {
                'position': params.position,
                'network_info': params.network_info
            }
        else:
            self.data.timestamps[timestamp] = {
                station_name: {
                    'position': params.position,
                    'network_info': params.network_info
                }
            }

        # Update latest_info map
        self.data.latest_info[station_name] = {
            'position': params.position,
            'network_info': params.network_info
        }

    @sp.effects(with_storage="read-only")
    def get_network_info(self, params):
        timestamp = params.timestamp
        station_name = params.station_name

        sp.result(self.data.timestamps.get(timestamp, {}).get(station_name, {}))

    @sp.effects(with_storage="read-only")
    def get_latest_network_info(self, params):
        station_name = params.station_name
        sp.result(self.data.latest_info.get(station_name, {}))

# Example usage
if "templates" not in __name__:
    @sp.add_test(name="NetworkInfoContract")
    def test():
        c = NetworkInfoContract()
        sp.add_message(c.store_network_info, {
            'timestamp': '2024-02-22 17:46:06',
            'station_name': 'sta1',
            'position': [24.67, 68.67, 0.0],
            'network_info': {
                'ip': '10.0.0.2/8',
                'channel': 1,
                'freq': 2.4,
                'mode': 'g',
                'encrypt': '',
                'passwd': None,
                'mac': '00:00:00:00:00:02'
            }
        })
        sp.add_message(c.store_network_info, {
            'timestamp': '2024-02-22 17:46:06',
            'station_name': 'sta2',
            'position': [62.08, 16.17, 0.0],
            'network_info': {
                'ip': '10.0.0.3/8',
                'channel': 1,
                'freq': 2.4,
                'mode': 'g',
                'encrypt': '',
                'passwd': None,
                'mac': '00:00:00:00:00:03'
            }
        })

        sp.add_message(c.get_network_info, {
            'timestamp': '2024-02-22 17:46:06',
            'station_name': 'sta1'
        })

        sp.add_message(c.get_latest_network_info, {
            'station_name': 'sta2'
        })

        scenario = sp.test_scenario()
        scenario += c
        scenario.h1("NetworkInfoContract")
        scenario.h2("Store Network Info")
        scenario += c
        scenario.h2("Get Network Info")
        scenario += c.get_network_info(
            timestamp='2024-02-22 17:46:06', station_name='sta1')
        scenario.h2("Get Latest Network Info")
        scenario += c.get_latest_network_info(station_name='sta2')