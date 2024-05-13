from scrapy.exceptions import DropItem,IgnoreRequest
class FrequentOperationError(IgnoreRequest):
    """自定义的异常类，继承自IgnoreRequest"""

    def __init__(self, message="frequent is operation"):
        self.message = message
        super().__init__(self.message)



