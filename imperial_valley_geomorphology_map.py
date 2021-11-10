import os
import pygmt
import pandas as pd
import geopandas as gpd    #python geospatial library
import re


# Figure Builder ======================================================
# class that contains the variables and functions that build the figures
class Figure_Builder():
    
    def __init__(self, main_dir, grid_clip_elevation):
        self.main_dir = main_dir
        self.grid_clip_elevation = grid_clip_elevation


    # plots maps using the clipped "elevations"
    def Plot_Clipped_Map(self):
        # Terrain Classification Data ======================================================
        # terrain classfication grids for the iwahashi et al. 2021 california terrain classification model
        terrainclass_grid_tif = os.path.join(main_dir, 'Data', 'California_NED_Classification_Iwahashi_etal_2021_Fig18_EPSG4326-WGS84.tif')

        # pulls the min and max of band 1 (terrain class in this case). nearest_multiple is the parameter that does this.
        raster_min_max = pygmt.grdinfo(terrainclass_grid_tif, nearest_multiple = True) 
        result = re.search('-T(.*)', raster_min_max)    # uses a regular expression to search the string for all characters after "-R" and groups them
        result = result.group(1)    # selects the desired string group
        raster_min_max = result.split('/')  # splits the group at each occurance of "/"
        raster_min_max = list(map(float, raster_min_max))   # maps the object to a list, preserving the float numbers of the lats and lons


        # PyGMT Maps ======================================================
        # Topographic Map ------------------------------------------------------
        hillshade_grid = os.path.join(main_dir, 'Data', 'Imperial-Valley_ASTER_DEM_merged_EPSG4326-WGS84.tif')
        # Terrain Classification Map ------------------------------------------------------
        transparency_terrainclass = 40   # transparency of the terrain classification map


        # Basemap ------------------------------------------------------
        region = [-116.95, -115.13, 32.7, 33.8] # Salton Sea region: [smallest lon, largest long, smallest lat, largest lat]
        projection = 'M6i' # map projection <type><size><units>
        frame = True    # sets frame ticks and spacing to be automatically determined


        # Coast ------------------------------------------------------
        #borders = ['1/0.8p,gray40', '2/0.8p,gray40'],   # sets board types to show and their attributes <type><thickness><color>
        shorelines = '1/0.5p,black'   # <type><thickness><color>
        resolution = 'f'    # sets the resolution of the coastlines (f = full, h = high, l = low)
        water = 'lightskyblue2' # sets the water color
        transparency_coast = '50'   # sets the transparency of the coast layer

        print('Plotting Map')

        for name, grid_clip in self.grid_clip_elevation.items():
            print('drawing:', name)

            fig = pygmt.Figure()

            # establishes base map which defines the basic framework of the map
            fig.basemap(
                region = region,    # sets the extent of the map area <min lon><max lon><min lat><max lat>
                projection = projection,   # sets the projection type for the map
                frame = frame, # sets the frame the boarders the map
            )

            # loads the hillshade basemap
            fig.grdimage(
                grid = hillshade_grid
            )
                

            # clips the terrain classification grid so that only desired terain classes are plotted
            # iterates over each selected terrain class and plots it.
            for i in grid_clip:
                # produces an elevation cliped version of the specified grid
                data_clip = pygmt.grdclip(
                    grid = terrainclass_grid_tif, # sets the grid data source
                    above = "{}/NaN".format(i), # sets all values above the current terrain class to be Nan
                    below = "{}/NaN".format(i)  # sets all values below the current terrain class to be Nan
                )

                # creates a color palette for the grid data
                pygmt.makecpt(
                    cmap = 'haxby', # sets the color palette
                    series = [raster_min_max[0], (raster_min_max[1]+1), 1] # sets the range of data for the color palette <min><max><step>
                )   

                # establishes the grid image to be plotted, in this case a terrain classification raster
                fig.grdimage(
                    grid = data_clip,   # source grid data
                    cmap = True,    # colors by color palette
                    nan_transparent = True, # makes Nan values transparent
                    transparency = transparency_terrainclass,    # sets layer transparency
                )
                    

            # estbalishes color bar for data
            fig.colorbar(
                frame = 'af+l"Terrain Class"',
                )

            
            # establishes the coastline and border layer
            fig.coast(
                borders = ['1/0.5p,gray40', '2/0.5p,gray40'],   # sets border attributes in this case national and state boundaries <border type>/<line thickness><line color>. For some reason can't pass a list variable to this parameter, so I wrote the list directly
                shorelines = shorelines,   # sets the shorline attributes
                resolution = resolution,   # sets the shoreline resolution attributes
                water = water, # sets the water attributes
                #transparency = transparency_coast,    # sets the layer transparency
            )
            
            # sets the save name of the map file
            map_save_name = os.path.join(self.main_dir, 'Results', 'Imperial-Valley_{}_Terrain_Class.png').format(name)

            # save the figure
            fig.savefig(map_save_name)

            # displays the plot in a pop-up or within a jupyter window (doesn't work on windows with a normal IDE)
            #plt.show()

# path to main directory
main_dir = r'/home/USER/Desktop/Imperial_Valley_Geomorphology_Map'
grid_clip_elevations = {'basin':[8, 16], 'basin_edge':[4, 7, 12, 14], 'mountain':[1, 2, 3, 5, 6, 9, 10, 11, 13, 15]} # selected terrain classifications, in this case those defining basins in the SFBA and LA regions

# initializes the Figure_Builder class
data = Figure_Builder(main_dir, grid_clip_elevations)
data.Plot_Clipped_Map()
