SOURCES = safe/__init__.py \
          safe/clipper.py \
          safe/dock.py \
          safe/impact_calculator.py \
          safe/impact_calculator_thread.py \
          safe/impact_functions_doc.py \
          safe/keyword_io.py \
          safe/keywords_dialog.py \
          safe/wizard_dialog.py \
          safe/options_dialog.py \
          safe/plugin.py \
          safe/utilities.py \
          realtime/shake_event.py

FORMS = safe/gui/ui/wizard_dialog_base.ui \
        safe/gui/ui/about_dialog_base.ui \
        safe/gui/ui/extent_selector_dialog_base.ui \
        safe/gui/ui/shakemap_importer_dialog_base.ui \
        safe/gui/ui/needs_manager_dialog_base.ui \
        safe/gui/ui/impact_report_dialog_base.ui \
        safe/gui/ui/function_browser_base.ui \
        safe/gui/ui/dock_base.ui \
        safe/gui/ui/options_dialog_base.ui \
        safe/gui/ui/function_browser_dialog_base.ui \
        safe/gui/ui/osm_downloader_dialog_base.ui \
        safe/gui/ui/impact_merge_dialog_base.ui \
        safe/gui/ui/function_options_dialog_base.ui \
        safe/gui/ui/keywords_dialog_base.ui \
        safe/gui/ui/batch_dialog_base.ui \
        safe/gui/ui/needs_calculator_dialog_base.ui


TRANSLATIONS = i18n/inasafe_id.ts \
               i18n/inasafe_af.ts
