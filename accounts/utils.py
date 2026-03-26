def es_comercio(user):
    return user.is_authenticated and user.groups.filter(name='usuario-comercio').exists()

def es_empleado(user):
    return user.is_authenticated and user.groups.filter(name='usuario-empleado').exists()