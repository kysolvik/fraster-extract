#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Functions for extracting raster values in buffer around points.

See:
    fraster_extract.py for usage
    examples/explore_buffer_extract.ipynb for info
"""


import os
import numpy as np
import rasterio as rio
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
import warnings


def _transform_x_to_lon(center_lat, buf_x):
    latlen = 111319.5
    lonlen = np.array(np.cos(center_lat*np.pi/180) * latlen)
    buf_x = buf_x[:, np.newaxis]/(lonlen)

    return buf_x


def _transform_y_to_lat(buf_y):
    return buf_y/111319.5


def _generate_points(radius=20, n=10000):
    """Takes <0.03 sec for 10,000 pts!"""
    t = 2 * np.pi * np.random.rand(n)
    r = np.random.rand(n)+np.random.rand(n)
    r[r > 1] = 2 - r[r > 1]
    pts = np.array([r * np.cos(t), r * np.sin(t)])*radius
    return pts


def _get_mean(band, cell_indices, cell_counts):
    # Outdated
    return np.average(band[cell_indices[0], cell_indices[1]],
                      weights=cell_counts)


def _get_all_cells(target_pts, sample_pts, ds, latlon=True):
    # This is the slowest section by far. Need to find a speed up
    if latlon:
        x = np.swapaxes(_transform_x_to_lon(target_pts.y, sample_pts[0])
                        + np.array(target_pts.x), 0, 1
                        ).flatten()

        temp_y_pts = _transform_y_to_lat(sample_pts[1])
        y = np.array([temp_y_pts + y for y in target_pts.y]).flatten()
    else:
        x = np.array([sample_pts[0] + x for x in target_pts.x]).flatten()
        y = np.array([sample_pts[1] + y for y in target_pts.y]).flatten()
    invtrans = ~ds.transform
    cols, rows = invtrans*(x, y)
    cells = np.array([rows, cols])
    cells = np.floor(cells).astype(int)
    return cells


def _extract_reshape_vals(band, cell_indices, n_sample):
    all_vals = band[cell_indices[0], cell_indices[1]]
    reshaped_vals = np.reshape(all_vals,
                               (len(cell_indices[0])//n_sample, n_sample)
                               )
    return reshaped_vals


def _get_all_mean_max(band, cell_indices, n_sample):
    reshaped_vals = _extract_reshape_vals(band, cell_indices, n_sample)
    avg = np.mean(np.unique(reshaped_vals, axis=1), axis=1)
    maxes = np.max(reshaped_vals, axis=1)
    return avg, maxes


def _get_all_mean(band, cell_indices, n_sample):
    reshaped_vals = _extract_reshape_vals(band, cell_indices, n_sample)
    avg = np.mean(np.unique(reshaped_vals, axis=1), axis=1)
    return avg


def _get_all_vals(band, cell_indices, n_sample, latlon=True):
    reshaped_vals = _extract_reshape_vals(band, cell_indices, n_sample)
    return reshaped_vals


def _full_pt_calc(target_pt, band, ds, sample_pts,
                  stat='mean_max', latlon=True):
    cells = _get_all_cells(target_pt, sample_pts, ds, latlon=latlon)
    if stat == 'mean_max':
        out = _get_all_mean_max(band, cells, sample_pts.shape[1])
    elif stat == 'mean':
        out = _get_all_mean(band, cells, sample_pts.shape[1])
    elif stat == 'all':
        out = _get_all_vals(band, cells, sample_pts.shape[1])
    elif stat == 'count_dict':
        vals = _get_all_vals(band, cells, sample_pts.shape[1])
        uniq_counts = [np.unique(vals[i], return_counts=True)
                       for i in range(vals.shape[0])]
        out = [dict(zip(u[0], u[1])) for u in uniq_counts]
    else:
        out = _get_all_vals(band, cells, sample_pts.shape[1])
        warnings.warn('Method not recognizable, returning all cell values')
    return out


def random_buffer_extract(gdf_coords, ds, radius=20, n_sample=1000, stat='mean',
                   latlon=True):
    sample_pts = _generate_points(radius, n_sample)
    band = ds.read(1)
    return _full_pt_calc(gdf_coords, band, ds, sample_pts, stat=stat,
                         latlon=latlon)


def gdf_random_buffer_extract(gdf_coords, ds, radius=20, n_sample=1000, stat='mean',
                       latlon=True):
    sample_pts = _generate_points(radius, n_sample)
    band = ds.read(1)
    return _full_pt_calc(gdf_coords, band, ds, sample_pts, stat=stat,
                         latlon=latlon)
        

