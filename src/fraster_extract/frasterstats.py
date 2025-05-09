#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extract raster values within buffered geometry centroids.

python3 frasterstats --help for list of args

Example Usage: 
    python3 frasterstats ../data/SJER_example.shp ../data/SJER_lidarCHM.tif ./output.csv 10 --not_latlon 
"""


import os
import glob
import geopandas as gpd
import re
import pandas as pd
import rasterio as rio
import argparse

from fraster_extract import _stats


def argparse_init():
    """Prepare ArgumentParser for inputs"""

    p = argparse.ArgumentParser(
            description='Run Random Buffer Extract on Shapefile',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    p.add_argument('shp',
        help = 'Path to shapefile with polygons or points',
        type = str)
    p.add_argument('raster',
        help = 'Path to raster, must be in WGS84 (lat/lon)',
        type = str)
    p.add_argument('output_csv',
        help = 'Path for output csv',
        type = str)
    p.add_argument('radius',
        help = 'Buffer radius, in meters',
        type = int)
    p.add_argument('--nsample',
        dest = 'n_sample',
        default = 1000,
        help = 'Number of random points to sample inside buffer.',
        type = int)
    p.add_argument('--stat',
        default = 'mean',
        choices = ['mean', 'mean_max', 'all', 'count_dict'],
        help = 'Statistic to calculate. One of: mean, mean_max, all, or count_dict',
        type = str)
    p.add_argument('--batch_size',
        default=10000,
        help = 'Batch size if many geometries. Default is 10000, anything less will run in a single batch',
        type = int)
    p.add_argument('--not_latlon',
        dest='latlon',
        action='store_false',
        help = 'Use this flag if the raster is NOT latlon and are already in meters instead')

    return(p)


def main():
    
    # Get Command Line Args
    parser = argparse_init()
    args = parser.parse_args()
     
    # Prep centroid dataframe
    gdf = gpd.read_file(args.shp)
    gdf['geometry'] = gdf['geometry'].centroid
    if args.latlon:
        gdf = gdf.to_crs('epsg:4326')

    batch_size = args.batch_size
    output_df = gdf.copy().drop(columns='geometry')
    ds = rio.open(args.raster)
    all_vals = []
    i = 0
    while i < gdf.shape[0]:
        end = min(i+batch_size, gdf.shape[0])
        all_vals += list(_stats.random_buffer_extract(gdf.iloc[i:end]['geometry'], ds, radius=args.radius, n_sample=args.n_sample,
                stat=args.stat, latlon=args.latlon))
        i+=batch_size

    output_df[os.path.splitext(os.path.basename(args.raster))[0] + '_' + args.stat] = all_vals

    output_df.to_csv(args.output_csv, index=False)


if __name__=='__main__':
    main()
