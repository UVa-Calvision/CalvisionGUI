
constexpr size_t N_Channels = 10;
constexpr size_t N_Samples = 1024;
constexpr float V_pp = 1000.0;
constexpr float DAC_size = 65535;
constexpr float ADC_size = 4095;

float dac_to_voltage(unsigned int dac) {
    return -V_pp * static_cast<float>(dac) / DAC_size;
}

float adc_to_voltage(unsigned int adc, unsigned int offset) {
    return V_pp * (-1.0 + static_cast<float>(adc) / ADC_size) + dac_to_voltage(offset);
}

unsigned int voltage_to_dac(float voltage) {
    return static_cast<unsigned int>(-DAC_size * voltage / V_pp);
}

unsigned int voltage_to_adc(float voltage, unsigned int offset) {
    return static_cast<unsigned int>(((voltage - dac_to_voltage(offset)) / V_pp + 1.0) * ADC_size);
}


class DrsOffsets {
public:
    DrsOffsets()
    {
        for (int i = 0; i < N_Channels; i++) {
            current_offsets_[i] = 0;
            new_offsets_[i] = 0;
        }
    }

    void set_current_offset_as_adc(int channel, unsigned int offset) {
        current_offsets_[channel] = offset;
    }

    unsigned int offset_as_adc(int channel) const {
        return new_offsets_[channel];
    }

    void load(const char* filename) {
        TChain* tree = new TChain("tree");
        tree->Add(filename);

        float channel_averages[N_Channels];
        for (int i = 0; i < N_Channels; i++)
            channel_averages[i] = 0;

        float channels[N_Channels][N_Samples];
        tree->SetBranchAddress("channels", &channels);
        for (UInt_t n = 0; n < tree->GetEntries(); n++) {
            tree->GetEntry(n);

            for (int i = 0; i < N_Channels; i++) {
                float sample_average = 0;
                for (int j = 0; j < 1024; j++) {
                    sample_average += channels[i][j];
                }
                channel_averages[i] += sample_average / 1024.0 / tree->GetEntries();
            }
        }

        for (int i = 0; i < N_Channels; i++) {
            std::cout << "Previous channel " << i << " offset: " << dac_to_voltage(current_offsets_[i]) << " mV\n";
            std::cout << "Channel " << i << " pedestal: " << channel_averages[i] << " mV\n";
            new_offsets_[i] = voltage_to_dac(dac_to_voltage(current_offsets_[i]) - channel_averages[i]);
            std::cout << "New channel " << i << " offsets: " << dac_to_voltage(new_offsets_[i]) << " mV\n";
        }
    }

private:

    unsigned int current_offsets_[N_Channels];
    unsigned int new_offsets_[N_Channels];
};
