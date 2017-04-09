import os
import hashlib
from trackhub import helpers

def test_example_data_md5s():
    data_dir = helpers.data_dir()

    data = [i.strip().split() for i in '''
    ba2fd8b22bcad65bb6583da937ff5222  newOrg1.2bit
    a6106256ee35e36f1ffa68f6543abf16  out.b
    a274a76ddfc2cb95e9db3751ca7cf82a  random-dm3-0.bigBed
    c680c1f5b4242634889011a0d2289112  random-dm3-1.bigBed
    797523ad6685db94044aebcfafc8fbec  random-dm3-2.bigBed
    604f2ca028f476bb0baf6da6aeca0901  random-no1-0.bigBed
    cdb1dc0d4a23980fed3e3b110aac635f  random-no1-1.bigBed
    f8efe813e570a896df2df625c14dd30c  random-no1-2.bigBed
    94cb83c18f73b713878c6ef28c19087d  sine-dm3-10000.bedgraph.bw
    968df78a8a18c6e7d5b061e92fde8d83  sine-dm3-1000.bedgraph.bw
    55ac2603c31b232dacfdaba07d8a25eb  sine-no1-1000.bedgraph.bw
    b8c983862c58fee6afa99382634ab2d8  sine-no1-100.bedgraph.bw
    '''.splitlines(False) if len(i.strip()) > 0]

    for md5, fn in data:
        assert (
            hashlib.md5(open(os.path.join(data_dir, fn), 'rb').read()).hexdigest() == md5
        ), 'md5sum mismatch for {}'.format(fn)
