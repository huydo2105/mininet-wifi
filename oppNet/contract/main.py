import smartpy as sp

@sp.module
def main():
    class NetworkInfoContract(sp.Contract):
        def __init__(self):
            self.data.timestamps = {}
            self.data.latest_infor = {}
            self.data.distances = {}
            
        @sp.entrypoint
        def store_distances_info(self, params):
            sp.cast(params, sp.record(staX=sp.string,
                                      staY=sp.string,
                                      distance=sp.string))
            self.data.distances = sp.update_map(
                    sp.record(staX = params.staX, staY = params.staY),
                    sp.Some(
                        params.distance
                    ),
                    self.data.distances
                )
            
        @sp.entrypoint
        def store_network_info(self, params):
            sp.cast(params, sp.record(timestamp=sp.string,
                                      station_name=sp.string,
                                      network_info=sp.map[sp.string, sp.string]))
            timestamp = params.timestamp
            station_name = params.station_name
            
            # Update timestamps map
            if self.data.timestamps.contains(timestamp):
                self.data.timestamps[timestamp][station_name] = {
                    'network_info': params.network_info
                }
            else:
                self.data.timestamps[timestamp] = {
                    station_name: {
                        'network_info': params.network_info
                    }
                }
                # Update latest_infor map
                self.data.latest_infor = sp.update_map(
                    station_name,
                    sp.Some(
                    {
                        'network_info': params.network_info
                    }),
                    self.data.latest_infor
                )

if "templates" not in __name__:
    @sp.add_test()
    def test():
        sc = sp.test_scenario("OppNet Test", main)
        c = main.NetworkInfoContract()
        sc += c

        sc.h1("NetworkInfoContract")
        sc.h2("Store Network Info")
        c.store_network_info(
            timestamp= '2024-02-22 17:46:06',
            station_name= 'sta1',
            network_info= {
                "position":"24.67, 68.67, 0.0",
                'ip': '10.0.0.2/8',
                'channel': "1",
                'freq': "2.4",
                'mode': 'g',
                'mac': '00:00:00:00:00:02'
            }
            
        )
        c.store_network_info (
            timestamp= '2024-02-22 17:46:06',
            station_name= 'sta2',
            network_info= {
                "position":"62.08, 16.17, 0.0",
                'ip': '10.0.0.3/8',
                'channel': "1",
                'freq': "2.4",
                'mode': 'g',
                'mac': '00:00:00:00:00:03'
            }
        )
        c.store_network_info (
            timestamp= '2024-02-22 17:46:06',
            station_name= 'sta2',
            network_info= {
                "position":"62.08, 16.17, 0.0",
                'ip': '10.0.0.3/8',
                'channel': "1",
                'freq': "2.4",
                'mode': 'g',
                'mac': '00:00:00:00:00:03'
            }
        )
        c.store_network_info (
            timestamp= '2024-02-22 17:46:06',
            station_name= 'sta3',
            network_info= {
                "position":"39.28, 53.06, 0.0",
                'ip': '10.0.0.4/8',
                'channel': "1",
                'freq': "2.4",
                'mode': 'g',
                'mac': '00:00:00:00:00:04'
            }
        )

        c.store_distances_info (
            staX = "sta1",
            staY = "sta2",
            distance = "64.47 meters"
        )