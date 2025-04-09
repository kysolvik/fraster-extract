[![DOI](https://zenodo.org/badge/117587281.svg)](https://zenodo.org/badge/latestdoi/117587281)

NOTE: WORK IN PROGRESS

# fraster-extract: Faster Raster Extract for circular buffers

fraster-extract is a lightweight Python package for quickly computing raster zonal statistics within circular buffers around points.

For installation and use instructions, [go to Quick Start](#quick-start).

## Why?

Calculating the zonal statistics in a circular buffer around a point is a very common geospatial analysis task. For example, you might have the point location of a building and want to know elevation and slope information around it. Or maybe you're looking at the land-use/land-cover information around thousands of dams.

**The problem:**: This is a *much* simpler task than the general zonal stats problem, which must be able to deal with any arbitrary polygon. However, current approaches don't leverage this extra information. Since we know the polygon for the zonal stats is an exact circle, we should be able outperform more general approaches, which typically use rasterization (see [rasterstats](https://pythonhosted.org/rasterstats/), a great package for calculating general zonal statistics). This means the process takes 3 steps:

1. Buffer points and store circular polygons.
2. Rasterize polygons to match raster resolution/projection.
3. Extract values from cells that overlap the rasterized circles. 

The behavior is not always predictable. Deciding which pixels are included in step 2 typically uses Bresenham's line algorithm, which does not always match what the user wants. For example, it'd be great if we could choose to include all raster pixels that touch the buffer *at all*. 

**The solution:** Knowing that the polygon is a perfect circle, we can use a Monte Carlo approach to randomly sample points within the circle, dramatically speeding up the process. The method needs 3 steps, each of which are much faster than the 3 steps in the general approach:
1. Generate points within random buffer (fast).
2. Extract values at those points (fast).

This also has the advantage of providing more predictable inclusion of pixels within the buffer. 

![image](https://github.com/user-attachments/assets/50bca067-36db-4e80-bb72-39d71534617f)


## Quick Start

### Installation

```
pip install fraster-extract
```

The examples/zonal-stats-comparisons.ipynb notebook also requires matplotlib and rasterstats:
```
pip install matplotlib rasterstats
```

### Usage

We recommend start with the examples/fraster-extract.ipynb, which walks you through using the module.

There are two ways to use fraster-extract:

1. Use the fraster_extract script:

```bash
fraster_extract points_df.shp raster.tif output.csv 10
```

You can also get more information by running
```bash
fraster_extract -h
```

3. Import the package and use in your own code:

```python
import fraster_extract as fe
import geopandas as gpd
import rasterio as rio

zonal_means = fe.random_buffer_extract()
```

## Extra information

- The general zonalstats approach and data was taken from Earth Lab: https://www.earthdatascience.org/courses/earth-analytics/remote-sensing-uncertainty/extract-data-from-raster/

- This started out as a final project for my advanced algorithms course. For a more detailed discussion of the problem and possible solutions, see the [presentation for that class](https://pythonhosted.org/rasterstats/)
