from .executable import Executable


class ZeroResultExecutable(Executable):
    def __init__(self, connectionHelper):
        super().__init__(connectionHelper, "Zero Result Executable")

    def is_attrib_all_null(self, Res, attrib):
        return self.isQ_result_empty(Res)

    def get_attrib_val(self, Res, attrib_idx):
        return Res[1][attrib_idx]

    def isQ_result_no_full_nullfree_row(self, Res):
        return self.isQ_result_empty(Res)

    def isQ_result_nonEmpty_nullfree(self, Res):
        return not self.isQ_result_empty(Res)

    def isQ_result_empty(self, Res):
        # self.logger.debug("exe: isQ_result_empty")
        check = False
        if len(Res) <= 1:
            return True
        if len(Res) == 2:
            data = Res[-1]
            check = all(val == '0' for val in data)
        return check

    def isQ_result_has_no_data(self, Res):
        return self.isQ_result_empty(Res)

    def isQ_result_all_null(self, Res):
        return self.isQ_result_empty(Res)

    def isQ_result_has_some_data(self, Res):
        return not self.isQ_result_empty(Res)