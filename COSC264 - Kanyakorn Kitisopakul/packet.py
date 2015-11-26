class Packet(object):

    def __init__(
        self,
        magicno,
        datatype,
        seqno,
        datalen,
        data,
        ):
        self.magicno = magicno
        self.datatype = datatype
        self.seqno = seqno
        self.datalen = datalen
        self.data = data

    def __str__(self):
        return 'Packet: ' + str(self.magicno) + ' ' \
            + str(self.datatype) + ' ' + str(self.seqno) + ' ' \
            + str(self.datalen) + ' ' + str(self.data) + ':Packet'



			