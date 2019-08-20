from os.path import dirname

import numpy as np
import redisai as rai
import ml2rt
import utils


class DB:

    def __init__(self, host='localhost', port=6379, db=0):
        self.max_len = 10
        self.con = rai.Client(host=host, port=port, db=db)

    def initiate(self):
        encoder_path = f'{dirname(__file__)}/assets/encoder.pt'
        decoder_path = f'{dirname(__file__)}/assets/decoder.pt'
        en_model = ml2rt.load_model(encoder_path)
        de_model = ml2rt.load_model(decoder_path)
        self.con.modelset('encoder', rai.Backend.torch, rai.Device.cpu, en_model)
        self.con.modelset('decoder', rai.Backend.torch, rai.Device.cpu, de_model)
        # 4 = no layers + no directions, 1 = batch, 500 = hidden size
        dummy_hidden = rai.BlobTensor.from_numpy(np.zeros((2, 1, 500), dtype=np.float32))
        self.con.tensorset('hidden', dummy_hidden)

    def process(self, nparray):
        tensor = rai.BlobTensor.from_numpy(nparray)
        self.con.tensorset('sentence', tensor)
        self.con.modelrun('encoder', input=['sentence', 'hidden'], output=['e_output', 'hidden'])
        sos_tensor = rai.BlobTensor.from_numpy(
            np.array(utils.SOS_token, dtype=np.int64).reshape(1, 1))
        self.con.tensorset('d_input', sos_tensor)
        i = 0
        out = []
        while i < self.max_len:
            i += 1
            self.con.modelrun(
                'decoder',
                input=['d_input', 'hidden', 'e_output'],
                output=['d_output', 'hidden'])
            d_output = self.con.tensorget('d_output', as_type=rai.BlobTensor).to_numpy()
            d_output_ret = d_output.reshape(1, utils.voc.num_words)
            ind = int(d_output_ret.argmax())
            if ind == utils.EOS_token:
                break
            inter_tensor = rai.Tensor(rai.DType.int64, shape=[1, 1], value=ind)
            self.con.tensorset('d_input', inter_tensor)
            if ind == utils.PAD_token:
                continue
            out.append(ind)
        return utils.indices2str(out)


if __name__ == '__main__':
    redis_db = DB()
