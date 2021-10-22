from configparser import ConfigParser
from Libraries.custom_errors import *

class Unmodifiable_Data():  # Reads the input parameters: checks their presence in the ini file, type and other options.
    def __init__(self, cfg: ConfigParser):
        self.cfg = cfg     
        self.__set_delta_z('simulation params', 'delta_z', float)
        self.__set_acceptance_rate('simulation params', 'acceptance_rate', float)
        self.__set_lag_time('simulation params', 'lag_time', float)
        self.__set_n_bins('plotting params', 'n_bins', int)
        self.__set_nbins_t('plotting params', 'nbins_t', int)
        self.__set_save_figures('plotting params', 'save_figures', bool)
        self.__set_plot_graphs('plotting params', 'plot_graphs', bool)
        self.__set_npy_directory('files and directories', 'npy_directory')    # If type not specified -> str
        self.__set_add_savefig_name('plotting params', 'add_savefig_name')
        self.__set_savefig_directory('plotting params', 'savefig_directory')
        self.__set_output_file('files and directories', 'output_file')
        
    def check_presence(self, section,parameter):
        if section not in self.cfg.sections():
            raise SectionNotPresentError(section)
        if parameter not in self.cfg[section]:
            raise ParameterNotPresentError(section, parameter)

    def check_type(self, section, parameter, expected_type):
        x = self.cfg.get(section, parameter)
        if (expected_type is float) or (expected_type is int):
            try:    
                expected_type(x)    # try conversion
            except ValueError:
                raise OptionError(parameter, msg = f'Error: Given {parameter} is not {expected_type.__name__}')
        elif expected_type is bool:
            if x.lower() not in {'true', 'false', '1', '0', 'on', 'off', 'yes', 'no'}:
                raise OptionError(parameter, msg = f"Error: Given {parameter} is not boolean. Possible values are: 'true', 'false', '1', '0', 'on', 'off', 'yes', 'no' (case insensitive).")
        elif expected_type is str:
            pass
        else:
            raise OptionError(parameter, msg = f'Error in the expected type of {parameter}: type not supported')

    def __set_delta_z(self, section, parameter_name, type):
        self.check_presence(section, parameter_name)
        self.check_type(section, parameter_name, type)
        self.__delta_z = self.cfg.getfloat(section, parameter_name)
        if self.__delta_z < 0:
            raise OptionError(parameter_name, f'Error: {parameter_name} must be positive.')
    def __get_delta_z(self):
        return self.__delta_z
    delta_z = property(__get_delta_z)
    
    def __set_acceptance_rate(self, section, parameter_name, type):
        self.check_presence(section, parameter_name)
        self.check_type(section, parameter_name, type)
        self.__acceptance_rate = self.cfg.getfloat(section, parameter_name)
        if not (0 <= self.__acceptance_rate <= 1.1):    # acceptance_rate == 1.1 is permitted for testing purposes
            raise OptionError(parameter_name, msg = f'Error: {parameter_name} must be between 0 and 1. (Also 1.1 is permitted for testing purposes)')
    def __get_acceptance_rate(self):
        return self.__acceptance_rate
    acceptance_rate = property(__get_acceptance_rate)

    def __set_lag_time(self, section, parameter_name, type):
        self.check_presence(section, parameter_name)
        self.check_type(section, parameter_name, type)
        self.__lag_time = self.cfg.getfloat(section, parameter_name)
        if self.__lag_time < 0:
            raise OptionError(parameter_name, msg = f'Error: {parameter_name} must be positive.')
    def __get_lag_time(self):
        return self.__lag_time
    lag_time = property(__get_lag_time)

    def __set_n_bins(self, section, parameter_name, type):
        self.check_presence(section, parameter_name)
        self.check_type(section, parameter_name, type)
        self.__n_bins = self.cfg.getint(section, parameter_name)
        if self.__n_bins < 0:
            raise OptionError(parameter_name, f'Error: {parameter_name} must be positive.') 
    def __get_n_bins(self):
        return self.__n_bins
    n_bins = property(__get_n_bins)

    def __set_nbins_t(self, section, parameter_name, type):
        self.check_presence(section, parameter_name)
        self.check_type(section, parameter_name, type)
        self.__nbins_t = self.cfg.getint(section, parameter_name)
        if self.__nbins_t < 0:
            raise OptionError(parameter_name, f'Error: {parameter_name} must be positive.') 
    def __get_nbins_t(self):
        return self.__nbins_t
    nbins_t = property(__get_nbins_t)

    def __set_plot_graphs(self, section, parameter_name, type):
        self.check_presence(section, parameter_name)
        self.check_type(section, parameter_name, type)
        self.__plot_graphs = self.cfg.getboolean(section, parameter_name) 
    def __get_plot_graphs(self):
        return self.__plot_graphs
    plot_graphs = property(__get_plot_graphs)

    def __set_save_figures(self, section, parameter_name, type):
        self.check_presence(section, parameter_name)
        self.check_type(section, parameter_name, type)
        self.__save_figures = self.cfg.getboolean(section, parameter_name) 
    def __get_save_figures(self):
        return self.__save_figures
    save_figures = property(__get_save_figures)

    def __set_npy_directory(self, section, parameter_name):
        self.check_presence(section, parameter_name)
        self.__npy_directory = self.cfg.get(section, parameter_name) 
    def __get_npy_directory(self):
        return self.__npy_directory
    npy_directory = property(__get_npy_directory)

    def __set_add_savefig_name(self, section, parameter_name):
        self.check_presence(section, parameter_name)
        self.__add_savefig_name = self.cfg.get(section, parameter_name) 
    def __get_add_savefig_name(self):
        return self.__add_savefig_name
    add_savefig_name = property(__get_add_savefig_name)

    def __set_savefig_directory(self, section, parameter_name):
        self.check_presence(section, parameter_name)
        self.__savefig_directory = self.cfg.get(section, parameter_name) 
    def __get_savefig_directory(self):
        return self.__savefig_directory
    savefig_directory = property(__get_savefig_directory)

    def __set_output_file(self, section, parameter_name):
        self.check_presence(section, parameter_name)
        self.__output_file = self.cfg.get(section, parameter_name) 
    def __get_output_file(self):
        return self.__output_file
    output_file = property(__get_output_file)