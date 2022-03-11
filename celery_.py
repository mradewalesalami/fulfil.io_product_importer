# # from celery import Celery
# # import celeryconfig
# #
# #
# # def make_celery(app):
# #     celery = Celery(app.import_name)
# #
# #     class ContextTask(celery.Task):
# #         def __call__(self, *args, **kwargs):
# #             with app.app_context():
# #                 return self.run(*args, **kwargs)
# #
# #     celery.Task = ContextTask
# #
# #     celery.config_from_object('celeryconfig')
# #
# #     return celery
#
# import flask
# from flask import current_app
# from celery import Celery
#
#
# class FlaskCelery(Celery):
#     def __init__(self, *args, **kwargs):
#
#         super(FlaskCelery, self).__init__(*args, **kwargs)
#         self.patch_task()
#         with current_app.app_context():
#             self.init_app(current_app)
#
#         # if 'app' in kwargs:
#         #     self.init_app(kwargs['app'])
#
#     def patch_task(self):
#         TaskBase = self.Task
#         _celery = self
#
#         class ContextTask(TaskBase):
#             abstract = True
#
#             def __call__(self, *args, **kwargs):
#                 if flask.has_app_context():
#                     return TaskBase.__call__(self, *args, **kwargs)
#                 else:
#                     with _celery.app.app_context():
#                         return TaskBase.__call__(self, *args, **kwargs)
#
#         self.Task = ContextTask
#
#     def init_app(self, app):
#         self.app = app
#         self.config_from_object(app.config)
#
#
# celery = FlaskCelery()