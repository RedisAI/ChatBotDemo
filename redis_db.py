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
        self.con.modelstore('encoder', backend='torch', device='cpu', data=en_model)
        self.con.modelstore('decoder', backend='torch', device='cpu', data=de_model)


    def process(self, nparray):
        # 4 = no layers + no directions, 1 = batch, 500 = hidden size
        # dummy_hidden = np.zeros((2, 1, 500), dtype=np.float32)
        # self.con.tensorset('hidden', tensor=dummy_hidden)
        self.con.tensorset('sentence', tensor=nparray)
        self.con.tensorset('length', tensor=np.array([nparray.shape[0]]).astype(np.int64))
        self.con.modelexecute('encoder', inputs=['sentence', 'length'], outputs=['e_output', 'hidden'])
        hidden = self.con.tensorget('hidden')[:2]
        self.con.tensorset('hidden', tensor=hidden)
        inter_tensor = np.array(utils.SOS_token, dtype=np.int64).reshape(1, 1)
        self.con.tensorset('d_input', tensor=inter_tensor)
        i = 0
        out = []
        while i < self.max_len:
            i += 1
            self.con.modelexecute(
                'decoder',
                inputs=['d_input', 'hidden', 'e_output'],
                outputs=['d_output', 'hidden'])
            d_output = self.con.tensorget('d_output')
            # d_output_ret = d_output.reshape(1, utils.voc.num_words)
            ind = int(d_output.argmax())
            if ind == utils.EOS_token:
                break
            inter_tensor = np.array(ind, dtype=np.int64).reshape(1, 1)
            self.con.tensorset('d_input', tensor=inter_tensor)
            if ind == utils.PAD_token:
                continue
            out.append(ind)
        return utils.indices2str(out)


if __name__ == '__main__':
    redis_db = DB()
