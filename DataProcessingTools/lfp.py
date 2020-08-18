from .objects import DPObject
import h5py
import scipy.signal as signal

class LFPData(DPObject):
    filename = "lowpass.mat"
    level = "channel"
    argsList = [("lowFreq",0.1), ("highFreq", 300.0), 
                ("filterName", "Butterworth"),
                ("filterOrder", 4)]

    def create(self, *args, **kwargs):
        dirs = kwargs.get("dirs")
        self.dirs = dirs
        if dirs != []:
            if self.args.filterName == "Butterworth":
                N = self.args.filterOrder
                b,a = signal.butter(N, [self.args.lowFreq, self.args.highFreq],
                                    "bandpass")
            else:
                raise(ValueError("Unknown filter type"))
            
            # TODO: get the data

    def load(self, fname=None):
        # override load since we want to use the already
        #  computed data from Julia
        if fname is None:
            fname = self.getfilename()
       
        with h5py.File(fname) as ff:
            _data = ff["lowpassdata/data"]
            self.data = _data["data"][:]
            self.filter_coefs = dict((k, v[:]) for (k, v) in
                                     _data["filter_coefs"].items())
            self.filter_name = bytes(_data["filter_name"][:]).decode('utf-16')
            self.filter_order = _data["filter_order"][:]
            self.low_freq = _data["low_freq"][:]
            self.high_freq = _data["high_freq"][:]
            self.sampling_rate = _data["sampling_rate"][:]
            self.channel = _data["channel"][:]
        


