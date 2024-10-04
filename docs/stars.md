# Big Sky Star Catalog

The Big Sky Star Catalog contains 2,557,499 stars compiled from the following catalogs: Hipparcos, Tycho-1, and Tycho-2. The position of each star is normalized to the J2000 Epoch, using the wonderful Python library [Skyfield](https://github.com/skyfielders/python-skyfield).

For complete details of how the Big Sky Star Catalog is created, check out [`bigsky/builders/stars.py`](../src/bigsky/builders/stars.py).

## Column Descriptions

### `tyc_id`

- _String_

- Tycho ID, formatted as a string with hyphens (e.g. 6-1005-1)

### `hip_id`

- _Integer_

- Hipparcos ID

### `ccdm`

- _String_

- CCDM Component Identifier (if applicable)

### `magnitude`

- _Float_

- Visual apparent magnitude (Johnson V)
- Rounded to two decimal places
- The Johnson V value is not in the Tycho-2 catalog directly, so the value in Big Sky is taken from Tycho-1 if available. For stars that are in Tycho-2 but not Tycho-1, then the following formula is used to convert Tycho-2's BT/VT magnitudes to Johnson V:

    V = VT - 0.090 * (BT-VT)

    \* Formula obtained from the Tycho-2 Readme
    
    \* _if BT or VT magnitude is not available for the star in Tycho-2, then the magnitude in Big Sky is listed as VT if that's available, otherwise it's listed as BT (one of these is always available in Tycho-2)_

### `bv`

- _Float_

- BV Color Index
- Rounded to two decimal places
- This is a calculated value from each star's VT/BT magnitudes, using the following formula:

    B-V = 0.850 * (BT-VT)

    \* Formula obtained from the Tycho-2 Readme

    \* If the star does not have a BT or VT value, then the B-V is listed as `null` in Big Sky

### `ra_degrees_j2000`

- _Float_

- Right Ascension in degrees (0 to 360) and Epoch J2000.0
- Rounded to four decimal places
- For stars from Tycho-2, this is the observed RA converted to the J2000 Epoch
- For stars from Hipparcos/Tycho-1, this is the listed RA from Tycho-2's supplement file, and converted to the J2000 Epoch

### `dec_degrees_j2000`

- _Float_

- Declination in degrees (-90 to 90) and Epoch J2000.0
- Rounded to four decimal places
- For stars from Tycho-2, this is the observed DEC converted to the J2000 Epoch
- For stars from Hipparcos/Tycho-1, this is the listed DEC from Tycho-2's supplement file, and converted to the J2000 Epoch

### `ra_mas_per_year`

- _Float_

- Rounded to two decimal places
- This value is from Tycho-2 if available for the star, otherwise it's taken from Tycho-1 if available there. If it's not listed in either catalog, then it will be listed as `0` in Big Sky.

### `dec_mas_per_year`

- _Float_

- Rounded to two decimal places
- This value is from Tycho-2 if available for the star, otherwise it's taken from Tycho-1 if available there. If it's not listed in either catalog, then it will be listed as `0` in Big Sky.

### `parallax_mas`

- _Float_

- Rounded to two decimal places
- This value is not available for any star in Tycho-2, so it's taken from Tycho-1 if available

### `name`

- _String_
- Name of the star, as designated by IAU
- Exception: the name listed for HIP 39953 is "Regor", in honor of astronauts :)

### `hd_id`

- _Integer_
- Henry Draper catalog number, if available

### `bayer`

- _String_
- Bayer designation, if available
- Only Greek letter designations are listed

### `flamsteed`

- _Integer_
- Flamsteed number, if available


## References
- [Hipparcos and Tycho Catalogues - VizieR](https://cdsarc.cds.unistra.fr/viz-bin/cat/I/239)
- [Tycho-2 Catalogue of the 2.5 Million Brightest Stars - VizieR](https://cdsarc.cds.unistra.fr/viz-bin/cat/I/259#/article)
- [Tycho-2 Catalogue Homepage](https://www.astro.ku.dk/~erik/Tycho-2/)
- [Construction and verification of the Tycho-2 Catalogue](https://ui.adsabs.harvard.edu/abs/2000A%26A...357..367H/abstract)
- [IAU-Catalog of Star Names](https://exopla.net/star-names/modern-iau-star-names/)
- [HD-DM-GC-HR-HIP-Bayer-Flamsteed Cross Index : IV/27A](https://cdsarc.u-strasbg.fr/viz-bin/Cat?IV/27A#/article)

## Spot an error?
If you see an error in any of this documentation or in the data itself, please open a GitHub issue about it. Your help is greatly appreciated!
