
import rasterio
import numpy as np
import matplotlib.pyplot as plt
import contextily as cx
from matplotlib.colors import ListedColormap
import rasterio
from pycaret.classification import *
from matplotlib import rcParams
import matplotlib.patches as mpatches

def visulization_plot(name=None, model=None, cleaned_data=None, all_data=None):

    pixel_indices = cleaned_data['pixel_index'].values

    # === Step 1: Predict on all valid pixels
    predictions = predict_model(model, data=cleaned_data.drop(columns=['Validation', 'pixel_index']))
    predicted_labels = predictions['prediction_label'].values

    # Safety check
    assert len(predicted_labels) == len(pixel_indices), "Mismatch between predictions and pixel indices"

    # === Step 5: Reconstruct prediction raster
    full_pred = np.full(len(all_data), -9999, dtype=np.int16)
    full_pred[pixel_indices] = predicted_labels

    # Save NumPy file
    np.save(f'./results/full_pred_{name}.npy', full_pred)

    # Load raster shape from a reference
    with rasterio.open(f'./results/{name}_validation_90m.tif') as ref:
        original_shape = (ref.height, ref.width)
        meta = ref.meta.copy()

    pred_raster = full_pred.reshape(original_shape)

    # Save prediction GeoTIFF
    meta.update(dtype='int16', count=1, nodata=-9999)
    with rasterio.open(f'./results/{name}_flood_prediction.tif', 'w', **meta) as dst:
        dst.write(pred_raster, 1)

    print(f"✅ Saved: {name}_flood_prediction.tif")

    tif_paths = {
        'Predicted': (f'./results/{name}_flood_prediction.tif', '#0000FF'),
        'Validation': (f'./results/{name}_validation_90m.tif', '#FF0000'),
    }

    fig, axes = plt.subplots(1, 2, figsize=(22, 10), dpi=300)

    for ax, (label, (tif_path, color)) in zip(axes, tif_paths.items()):
        with rasterio.open(tif_path) as src:
            flood = src.read(1)
            crs = src.crs
            nodata = src.nodata if src.nodata is not None else -9999
            flood = np.where(flood == nodata, np.nan, flood)
            extent = [
                src.bounds.left,
                src.bounds.right,
                src.bounds.bottom,
                src.bounds.top,
            ]

        ax.set_xlim(extent[0], extent[1])
        ax.set_ylim(extent[2], extent[3])
        cx.add_basemap(ax, crs=crs, source=cx.providers.OpenStreetMap.Mapnik)

        cmap = ListedColormap(['white', color])
        ax.imshow(flood, cmap=cmap, extent=extent, origin='upper', alpha=1, zorder=10)
        ax.set_axis_off()
        ax.set_title(label, fontsize=14, fontweight='bold')

    # Shared legend
    legend_handles = [
        mpatches.Patch(color='#0000FF', label='Predicted Flood'),
        mpatches.Patch(color='#FF0000', label='Validation Flood'),
    ]
    fig.legend(
        handles=legend_handles,
        loc='lower center',
        ncol=2,
        fontsize=12,
        frameon=True,
        bbox_to_anchor=(0.5, 0.01),
    )

    # plt.suptitle(f"{name} Flood Map Comparison", fontsize=16, fontweight='bold', y=1.01)
    plt.tight_layout()
    plt.savefig(f'./results/{name}_flood_comparison.png', dpi=300, bbox_inches='tight')
    plt.show()        

def metric_plot(results_01=None, results_02=None):

    from matplotlib import rcParams

    # Set Arial font globally
    rcParams['font.family'] = 'Arial'

    # --- Config ---
    metrics = ['CSI', 'F1', 'Recall']
    row_01 = results_01.iloc[0]
    row_02 = results_02.iloc[0]
    values_01 = [row_01[m] for m in metrics]
    values_02 = [row_02[m] for m in metrics]

    # --- Plot ---
    y = np.arange(len(metrics))
    height = 0.35
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')
    bars1 = ax.barh(y + height/2, values_01, height=height, color='red', label='Train on One', zorder=2)
    bars2 = ax.barh(y - height/2, values_02, height=height, color='blue',    label='Train on Two', zorder=2)

    # for bar, val in zip(bars1, values_01):
    #     ax.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height() / 2,
    #             f'{val:.2f}', va='center', fontsize=10)
    # for bar, val in zip(bars2, values_02):
    #     ax.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height() / 2,
    #             f'{val:.2f}', va='center', fontsize=10)

    ax.set_yticks(y)
    ax.set_yticklabels(metrics, fontsize=10, fontweight='normal')
    ax.set_xlim(0, 1.0)
    ax.set_xlabel('Score',  fontsize=14, fontweight='bold')
    ax.set_ylabel('Metric', fontsize=14, fontweight='bold')
    ax.set_title('Best Model Comparison', fontsize=15, fontweight='bold', pad=15)
    ax.tick_params(axis='both', direction='in', length=5, width=1.2, colors='black', zorder=5)
    ax.xaxis.grid(True, linestyle='--', linewidth=0.8, color='lightgray', zorder=4)
    ax.yaxis.grid(True, linestyle='--', linewidth=0.8, color='lightgray', zorder=4)
    ax.set_axisbelow(False)

    for spine in ['bottom', 'left']:
        ax.spines[spine].set_linewidth(1)
        ax.spines[spine].set_color('black')
        ax.spines[spine].set_zorder(5)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    ax.legend(title='Model', fontsize=10, title_fontsize=11,
            loc='upper right', frameon=True, framealpha=1, edgecolor='lightgray')

    plt.tight_layout()
    plt.savefig('model_comparison.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.show()