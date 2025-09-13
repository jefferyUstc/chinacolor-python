# ChinaColor-python

Chinese traditional colors and palettes for matplotlib/seaborn. The Python Version of [chinacolor](https://github.com/zhiming-chen/chinacolor)

## Features
- [384 traditional colors](https://htmlpreview.github.io/?https://github.com/jefferyUstc/chinacolor-python/blob/main/checklist/colors.html)
- [60 predefined palettes](https://htmlpreview.github.io/?https://github.com/jefferyUstc/chinacolor-python/blob/main/checklist/palettes.html) (sequential/diverging/qualitative)
- Utilities to get palettes as color lists or matplotlib colormaps
- Helper plotting to preview palettes
  - `plot_palette`, `plot_palettes`, `plot_color_grid`
- DataFrame helpers (require pandas): `colors_df()`, `palettes_df()`, alias `list_colors()`
- Themes for matplotlib/seaborn: `theme_ctc_paper`, `theme_ctc_mineral`, `theme_ctc_ink`, `theme_ctc_bronze`, `theme_ctc_dunhuang`
- Recommended palettes per-theme (categorical/sequential/diverging)

## Install (local)
- From this folder: `pip install -e .[seaborn]`
- With pandas helpers: `pip install -e .[pandas,seaborn]`

## Quickstart
```python
import chinacolor as ctc
from matplotlib import pyplot as plt

# Discrete palette for categorical hue
colors = ctc.get_palette("qual15", n=6)

# Continuous colormap for scalar values
cmap = ctc.get_cmap("seq05")

# Seaborn usage
import seaborn as sns
ax = sns.scatterplot(data=sns.load_dataset("iris"), x="sepal_length", y="sepal_width", hue="species", palette=colors)

# Matplotlib with colormap
import numpy as np
Z = np.random.RandomState(0).randn(50, 50)
plt.imshow(Z, cmap=ctc.get_cmap("div13", direction=-1))

# Preview a palette
ctc.plot_palette("seq08")
```
