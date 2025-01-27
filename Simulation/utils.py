import json

class Encodable:
    def toJSON(self):
        return json.dumps(self.toObject(), default=str)
    
    def toObject(self):
        # This breaks in infinite recursion if there are circular refs
        # overload this method with your custom serialization
        obj = { key:self.serialize(val) for key, val in self.__dict__.items() }
        return obj
    
    @staticmethod
    def serialize(obj):
        if isinstance(obj, Encodable):
            return obj.toObject()
        
        elif isinstance(obj, (list, tuple)):
            return [Encodable.serialize(x) for x in obj]
        
        elif isinstance(obj, dict):
            return { key:Encodable.serialize(val) for key, val in obj.items() }

        return obj