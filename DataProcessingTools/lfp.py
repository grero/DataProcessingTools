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
        
    def filter(self, lowfreq, highfreq,
            filter_name="Butterworth", filter_order=4):
        """
        Create a new LFP object from the current one by applying
        the supplied filter
        """
        if filter_name == "Butterworth":
            N = filter_order
            fs = self.sampling_rate
            b, a = signal.butter(N, [lowfreq/fs, highfreq/fs],
                                 "bandpass")
        else:    
            raise(ValueError("Unknown filter type"))

        fdata = signal.filtfilt(b, a, self.data)

        # crete an empty object
        lfpdata = LFPData(dirs=[])
        lfpdata.data = fdata
        lfpdata.filtet_coefs = {}
        lfpdata.filter_name = filter_name
        lfpdata.filter_order = filter_order
        lfpdata.low_freq = lowfreq
        lfpdata.high_freq = highfreq
        lfpdata.sampling_rate = self.sampling_rate
        lfpdata.channel = self.channel

        return lfpdata
