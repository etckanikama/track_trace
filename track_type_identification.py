import geopandas

url = "./content/asaka-detection-2021-10-06-02-15.geojson"
plot_data = geopandas.read_file(url)

for i in range(len(plot_data)):
    p = plot_data.iloc[i].track_id
    print(p)
    