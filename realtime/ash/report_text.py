# coding=utf-8

from PyQt4.QtCore import QObject

__author__ = 'Rizky Maulana Nugraha <lana.pcfre@gmail.com>'
__date__ = '2/11/2017'


class ReportText(QObject):
    """Placeholder class for texts in the report."""

    def __init__(self):
        QObject.__init__(self)

    def qpt_token(
            self,
            volcano_name=None, timestamp_string=None, region=None,
            alert_level=None, longitude_string=None, latitude_string=None,
            eruption_height=None, elapsed_hour=None, elapsed_minute=None,
            version=None):
        """Token string for QPT template"""
        event = {
            'report-title': self.tr('Volcanic Ash Impact'),
            'report-timestamp': self.tr('Volcano: %s, %s') % (
                volcano_name,
                timestamp_string),
            'report-province': self.tr('Province: %s') % (region,),
            'report-alert-level': self.tr('Alert Level: %s') % (
                alert_level.capitalize(),),
            'report-location': self.tr(
                'Position: %s, %s;'
                ' Eruption Column Height (a.s.l) - %d m') % (
                                   longitude_string,
                                   latitude_string,
                                   eruption_height),
            'report-elapsed': self.tr(
                'Elapsed time since event: %s hour(s) and %s minute(s)') % (
                                  elapsed_hour, elapsed_minute),
            'header-impact-table': self.tr(
                'Potential impact at each fallout level'),
            'header-nearby-table': self.tr('Nearby places'),
            'header-landcover-table': self.tr('Land Cover Impact'),
            'content-disclaimer': self.tr(
                'The impact estimation is automatically generated and only '
                'takes into account the population, cities and land cover '
                'affected by different levels of volcanic ash fallout at '
                'surface level. The estimate is based on volcanic ash '
                'fallout data from Badan Geologi, population count data '
                'derived by DMInnovation from worldpop.org.uk, place '
                'information and land cover classification data provided by '
                'Indonesian Geospatial Portal at http://portal.ina-sdi.or.id '
                'and software developed by BNPB. Limitation in the estimates '
                'of surface fallout, population and place names datasets may '
                'result in a significant misrepresentation of the '
                'on-the-surface situation in the figures shown here. '
                'Consequently, decisions should not be made solely on the '
                'information presented here and should always be verified '
                'by ground truthing and other reliable information sources.'
            ),
            'content-notes': self.tr(
                'This report was created using InaSAFE version %s. Visit '
                'http://inasafe.org for more information. ') % version,
            'content-support': self.tr(
                'Supported by DMInnovation, Geoscience Australia and the World Bank-GFDRR')
        }
        return event

    def population_table_token(self):
        table_header = [
            {
                'header': self.tr('Fallout Level')
            },
            {
                'header': self.tr('Very Low'),
                'class': 'lv1'
            },
            {
                'header': self.tr('Low'),
                'class': 'lv2'
            },
            {
                'header': self.tr('Moderate'),
                'class': 'lv3'
            },
            {
                'header': self.tr('High'),
                'class': 'lv4'
            },
            {
                'header': self.tr('Very High'),
                'class': 'lv5'
            },
        ]

        potential_impact_header = [
            self.tr('Potential Impact'),
            self.tr('Impact on health (respiration), livestock, and contamination of water supply.'),
            self.tr('Damage to transportation routes (e.g. airports, roads, railways); damage to critical infrastructure (e.g. electricity supply); damage to more vulnerable agricultural crops (e.g. rice fields)'),
            self.tr('Damage to less vulnerable agricultural crops (e.g. tea plantations) and destruction of more vulnerable crops; destruction of critical infrastructure; cosmetic (non-structural) damage to buildings'),
            self.tr('Dry loading on buildings causing structural damage but not collapse; Wet loading on buildings (i.e. ash loading + heavy rainfall) causing structural collapse.'),
            self.tr('Dry loading on buildings causing structural collapse.')
        ]

        context = {
            'table_header': table_header,
            'affected_header': self.tr('Estimated People Affected'),
            'potential_impact_header': potential_impact_header,
            'ash_thickness_header': self.tr('Ash Thickness Range (cm)')
        }
        return context

    def landcover_table_token(self, landcover_list=None):
        # Landcover type localization for dynamic translations:
        # noqa
        landcover_types = [
            self.tr('Forest'),
            self.tr('Plantation'),
            self.tr('Water Supply'),
            self.tr('Settlement'),
            self.tr('Rice Field')
        ]

        context = {
            'landcover_list': landcover_list,
            'landcover_type_header': self.tr('Land Cover Type'),
            'landcover_area_header': self.tr('Area affected (km<sup>2</sup>)'),
            'empty_rows': self.tr('No area affected')
        }

        return context

    def hazard_label_token(self):
        return {
            0: self.tr('Very Low'),
            1: self.tr('Low'),
            2: self.tr('Moderate'),
            3: self.tr('High'),
            4: self.tr('Very High')
        }

    def nearby_table_token(self, item_list=None):
        return {
            'item_list': item_list,
            'name_header': self.tr('Name'),
            'affected_header': self.tr('People / Airport affected'),
            'fallout_header': self.tr('Fallout Level'),
            'empty_rows': self.tr('No nearby cities or airport affected')
        }

