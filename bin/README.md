## Installation
Install on Ubuntu by:
1. Adding InaSAFE path to environment e.g:

   ```export InaSAFEQGIS=/home/akbar/dev/python/inasafe-dev/```
   
2. Adding QGIS to environment, or simply by updating run-env-linux.sh as necessary and run:
   
   ```source run-env-linux.sh```
   
3. Making inasafe CLI executable:
   
   ```chmod ug+x inasafe```
   
4. Soft-linking executable inasafe CLI to bin:
   
   ```sudo ln -s `pwd`/inasafe  /usr/bin```

## USAGE EXAMPLES
### Downloading exposures

```inasafe --download --feature-type=buildings --extent=106,84:-6,2085970:106,8525945:-6,1876174 --output-dir=/home/akbar/dev/data/test_cli/```

### Running scenario
- Downloading the exposure on the fly:

```inasafe --hazard=safe/test/data/gisv4/hazard/tsunami_vector.geojson --download --feature-type=buildings  --output-dir=/home/akbar/dev/data/test_cli/ --extent=106,7999364:-6,2085970:106,8525945:-6,1676174```

- Specifying the exposure:

```inasafe --hazard=safe/test/data/gisv4/hazard/tsunami_vector.geojson --exposure=safe/test/data/gisv4/exposure/raster/population.asc  --output-dir=/home/akbar/dev/data/test_cli/ --extent=106,7999364:-6,2085970:106,8525945:-6,1676174```
