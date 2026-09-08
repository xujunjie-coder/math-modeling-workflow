"""
scipilot-figure: Dual-Track Publication-Grade Export Module
Saves high-resolution PNG (300+ DPI) and vector PDF figures to designated project directories.
"""

import os
import shutil
import matplotlib.pyplot as plt

def export_figure(fig, fig_name, dpi=300, save_pdf=False, target_subdirs=None):
    """
    Save figure across standard project locations with quality verification.
    
    Parameters:
    - fig: matplotlib Figure object
    - fig_name: filename with extension (e.g. 'fig1_kinetics.png')
    - dpi: resolution, minimum 300
    - save_pdf: whether to also output vector PDF
    - target_subdirs: list of target directories. Defaults to ['paper/figures', 'paper/latex/figures']
    """
    if target_subdirs is None:
        target_subdirs = [
            "paper/figures",
            "paper/latex/figures"
        ]
        
    base_name = os.path.splitext(fig_name)[0]
    exported_paths = []
    
    for sdir in target_subdirs:
        os.makedirs(sdir, exist_ok=True)
        
        # PNG export
        png_path = os.path.join(sdir, f"{base_name}.png")
        fig.savefig(png_path, dpi=dpi, bbox_inches='tight')
        exported_paths.append(png_path)
        
        # Vector PDF export if requested
        if save_pdf:
            pdf_path = os.path.join(sdir, f"{base_name}.pdf")
            fig.savefig(pdf_path, format='pdf', bbox_inches='tight')
            exported_paths.append(pdf_path)
            
    print(f"[SciPilot Figure] Successfully exported figure '{base_name}' ({dpi} DPI) to:")
    for p in exported_paths:
        file_size_kb = os.path.getsize(p) / 1024
        print(f"  - {p} ({file_size_kb:.1f} KB)")
        
    return exported_paths

if __name__ == '__main__':
    # Unit test with simple plot
    from setup_style import set_sci_style, SCI_PALETTE
    set_sci_style()
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot([1, 2, 3], [4, 5, 6], color=SCI_PALETTE[0], label='Test Curve')
    ax.legend()
    ax.set_title('SciPilot Export Test')
    export_figure(fig, "test_export.png")
    plt.close()
