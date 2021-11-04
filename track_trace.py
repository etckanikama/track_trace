import geopandas
import folium
import matplotlib.cm as cm
import matplotlib.colors as colors
import matplotlib.pyplot as plt
from mapclassify import classify
from shapely.geometry import Point, LineString, Polygon
from  decimal import * 
import math 
import pandas as pd 
import numpy as np


url = "./content/asaka-detection-2021-10-06-02-15.geojson"
plot_data = geopandas.read_file(url)
# QGIS側のcoodinate(x,y)にあたる

pointA = Point(139.616880,35.809627)
pointB = Point(139.617143,35.809727)
pointC = Point(139.617114,35.809787)
pointD = Point(139.616855,35.809693)

# 外積のチェック
# AB，DC間で正なら内側
# AD,BC間で負なら内側

# 外積を求めるプログラム
def CrossProduct(pt1_x, pt1_y,pt2_x, pt2_y, pt_x, pt_y):
  ans = (pt2_x - pt1_x)*(pt_y - pt1_y) - (pt2_y - pt1_y)*(pt_x - pt1_x)
  return ans 

count = 0
n = 6 #小数点n桁以下を切り捨て

# AB間のみ
AB_dict = {}
AB_time_dict ={}
AB_line ={}
AB_line_time ={}
ans_dict = {}
AB_in = {}
AB_in_time = {}
for i in range(len(plot_data)):
  # print(plot_data.iloc[i].geometry)
  plot_data_x = plot_data.iloc[i].geometry.x #POINTのx座標にアクセス
  plot_data_y = plot_data.iloc[i].geometry.y
  
  plot_data_x = math.floor(plot_data_x * 10 ** n) /(10**n)
  plot_data_y = math.floor(plot_data_y * 10 ** n) /(10**n)
  ans = CrossProduct(pointA.x, pointA.y, pointB.x, pointB.y, plot_data_x, plot_data_y)
  
  if ans > 0: #外積を用いて線上を含めた内側の時間と座標を保持する
    ans_dict[i] = ans
    AB_dict[i] = Point(plot_data_x, plot_data_y)
    AB_time_dict[i] = plot_data.iloc[i].timestamp
    count += 1
#ans_dict_sorted：時間でソートし早い方から100個のデータを取り出す
ans_dict_sorted = sorted(ans_dict.items(), key=lambda x:x[1])[:100]
# ans_dict_key_sorted = sorted(ans_dict.items(), key=lambda x:x[0])[:100]

for i,(key,value) in enumerate(AB_dict.items()):#key:何番目の値かどうか，value:座標
  for j,tp in enumerate(ans_dict_sorted):#j:index, tp[0]:ans_dict_sortedのkey
    # print(i,j[0])
    if key == tp[0]:
      AB_line[key] = Point(AB_dict[key].x,AB_dict[key].y) 
      AB_line_time[key] = plot_data.iloc[key].timestamp
    else:
      AB_in[key] = Point(AB_dict[key].x,AB_dict[key].y)
      AB_in_time[key] = plot_data.iloc[key].timestamp


# sampleDataFrame = pd.DataFrame(
#     {"number":[key for key,value in AB_line.items()],
#      "geometry":[value for key,value in AB_line.items()]}
# )
# gdf = geopandas.GeoDataFrame(sampleDataFrame)
# print(gdf)
# gdf.to_file("check_trace_data_line.geojson",driver="GeoJSON")



BC_dict = {}
BC_time_dict = {}

cnt = 0
for i,(key,value) in enumerate(AB_in.items()):
  ans = CrossProduct(pointB.x, pointB.y, pointC.x, pointC.y, AB_in[key].x, AB_in[key].y)
  if ans >= 0:
    BC_dict[key] = Point(AB_in[key].x,AB_in[key].y) 
    BC_time_dict[key] = AB_in_time[key]
    cnt +=1


DC_dict = {}
DC_time_dict = {}
DC_line = {}
DC_line_time = {}
dc_ans_dict = {}
DC_in = {}
DC_in_time = {}
cn = 0
for i,(key,value) in enumerate(BC_dict.items()):
  ans = CrossProduct(pointD.x, pointD.y, pointC.x, pointC.y, BC_dict[key].x, BC_dict[key].y)
  if ans < 0:
    dc_ans_dict[key] = ans
    DC_dict[key] = Point(BC_dict[key].x, BC_dict[key].y) 
    DC_time_dict[key] = BC_time_dict[key]
    cn +=1

dc_ans_dict_sorted = sorted(dc_ans_dict.items(), key=lambda x:x[1])[:100]
for i,(key,value) in enumerate(DC_dict.items()):
  for j,tp in enumerate(dc_ans_dict_sorted):

    if key == tp[0]:
      DC_line[key] = Point(DC_dict[key].x,DC_dict[key].y) 
      DC_line_time[key] = plot_data.iloc[key].timestamp
    else:
      DC_in[key] = Point(DC_dict[key].x,DC_dict[key].y)
      DC_in_time[key] = plot_data.iloc[key].timestamp

# # DA_dict = {}
# # DA_time_dict = {}
# # c = 0
# # for i,(key,value) in enumerate(DC_dict.items()):
# #   ans = CrossProduct(pointD.x, pointD.y, pointA.x, pointA.y, DC_dict[key].x, DC_dict[key].y)
# #   if ans <= 0:
# #     DA_dict[key] = Point(DC_dict[key].x,DC_dict[key].y) 
# #     DA_time_dict[key] = DC_time_dict[key]
# #     c +=1



mm = AB_line
data_time = AB_in_time
data_plot = AB_in

M_dict = {}
distance = {}
M0_index = sorted(AB_line_time.items(), key=lambda x:x[0])[0][0]
Mn_index = sorted(DC_line_time.items(), key=lambda x:x[0])
next_point = []
next_point.append(M0_index)

for i,(key0,value0) in enumerate(DC_in.items()):
  for j, (key1, value1) in enumerate(AB_line.items()):
    distance[key0] = math.sqrt((AB_line[M0_index].x - value0.x)**2 + (AB_line[M0_index].y - value0.y)**2)

distance_sorted = sorted(distance.items(), key=lambda x:x[1])   
for data in distance_sorted:
  if data[1] != 0.0:
    next_point.append(data[0])
    M0_index = data[0]
    break

L = math.sqrt((pointC.x - pointB.x)**2 + (pointC.y - pointB.y)**2)
M0 = 0
gain_distance = 0
time = 0
while L >= gain_distance:
  new_distance = {}
  for j, (key1, value1) in enumerate(DC_in.items()):
    new_distance[key1] = math.sqrt((DC_in[M0_index].x - value1.x)**2 + (DC_in[M0_index].y - value1.y)**2)

  new_distance_sorted = sorted(new_distance.items(), key=lambda x:x[1])
  for i,data in enumerate(new_distance_sorted):
      if data[0] not in next_point and data[1] != 0.0: 
        next_point.append(data[0])

        M0_index = data[0]
        break

  try:
    time += float(DC_time_dict[next_point[M0]][17:26])
  except:
    pass
  M1 = M0
  M0 += 1
  gain_distance += math.sqrt((DC_dict[next_point[M0]].x - DC_dict[next_point[M1]].x)**2 + (DC_dict[next_point[M0]].y - DC_dict[next_point[M1]].y)**2)



print("トラックの通過時間",time/360)
# print(gain_distance)
# print(L)
