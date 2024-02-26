import smartpy as sp

tstorage = sp.record(distances = sp.map(sp.record(staX = sp.string, staY = sp.string).layout(("staX", "staY")), sp.string), latest_infor = sp.map(sp.string, sp.map(sp.string, sp.map(sp.string, sp.string))), timestamps = sp.map(sp.string, sp.map(sp.string, sp.map(sp.string, sp.map(sp.string, sp.string))))).layout(("distances", ("latest_infor", "timestamps")))
tparameter = sp.variant(store_distances_info = sp.record(distance = sp.string, staX = sp.string, staY = sp.string).layout(("distance", ("staX", "staY"))), store_network_info = sp.record(network_info = sp.map(sp.string, sp.string), station_name = sp.string, timestamp = sp.string).layout(("network_info", ("station_name", "timestamp")))).layout(("store_distances_info", "store_network_info"))
tprivates = { }
tviews = { }
