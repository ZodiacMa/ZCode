#-*-coding:utf-8-*- 
from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin
from django.conf import settings


POST_STATUS_CHOICES = (
    (0, u"公开"),
    (1, u"私人"),
    (2, u"草稿"),
    (3, u"垃圾箱"),
)

COMMENT_STATUS_CHOICES = (
    (0, u"开放"),
    (1, u"关闭"),
)

class Category(models.Model):
    """
    Category
    """
    
    name            = models.CharField(u"名称", unique=True, max_length=30)
    parent          = models.ForeignKey("self", null=True, blank=True, related_name=u"children")
    
    def get_separator(self):
        return ' --> '
    
    def get_path(self, **kwargs):
        return Category.objects.get_path(self, **kwargs)
    
    def get_tree(self, **kwargs):
        return Category.objects.get_tree(self, **kwargs)
    
    def num_descendants(self):
        return Category.objects.num_descendants(self)
    
    def _recurse_for_parents(self, cat_obj):
        p_list = []
        if cat_obj.parent_id:
            p = cat_obj.parent
            p_list.append(p.name)
            more = self._recurse_for_parents(p)
            p_list.extend(more)
        if cat_obj == self and p_list:
            p_list.reverse()
        return p_list
    
    def _parents_repr(self):
        p_list = self._recurse_for_parents(self)
        return self.get_separator().join(p_list)
    _parents_repr.short_description = u"父级类别"
    
    def _pre_save(self):
        p_list = self._recurse_for_parents(self)
        if self.category_name in p_list:
            raise u"You must not save a category in itself!"
        
    def __repr__(self):
        p_list = self._recurse_for_parents(self)
        p_list.append(self.category_name)
        return self.get_separator().join(p_list)
    
    def __unicode__(self):
        p = self._parents_repr()
        if p:
            return self.get_separator().join([
                    p, self.name])
        else:
            return self.name
    
    class Meta:
        verbose_name = u"分类"
        verbose_name_plural = u"分类列表"
        

class Tag(models.Model):
    """
    Tags
    """
    
    name        = models.CharField(u"名称", unique=True, max_length=30)
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        verbose_name = u"标签"
        verbose_name_plural = u"标签列表"
    

class Post(models.Model):
    """
    Post
    """
    
    title           = models.CharField(u"标题", max_length=100)
    status          = models.SmallIntegerField(u"状态", choices=POST_STATUS_CHOICES, default=0)
    category        = models.ManyToManyField(Category, null=True, blank=True, verbose_name=u"分类")
    content         = models.TextField(u"内容")
    create_time     = models.DateTimeField(u"创建时间", auto_now_add=True)
    update_time     = models.DateTimeField(u"更新时间", auto_now=True)
    tags            = models.ManyToManyField(Tag, verbose_name=u"标签")
    comment_status  = models.SmallIntegerField(u"评论状态", choices=COMMENT_STATUS_CHOICES, default=0)
    
    class Meta:
        verbose_name = u"日志"
        verbose_name_plural = u"日志列表"

    def get_absolute_url(self):
        return "/post/%i/" % self.id
         
    def __unicode__(self):
        return self.title
    
def make_publish(self, request, queryset):
    rows_updated = queryset.update(status=0)
    message_bit = u"%s篇日志被发布" % rows_updated
    self.message_user(request, message_bit)

def make_private(self, request, queryset):
    rows_updated = queryset.update(status=1)
    message_bit = u"%s篇日志被列为私人日志" % rows_updated
    self.message_user(request, message_bit)
    
def make_draft(self, request, queryset):
    rows_updated = queryset.update(status=1)
    message_bit = u"%s篇日志被列为草稿" % rows_updated
    self.message_user(request, message_bit)
    
def make_trash(self, request, queryset):
    rows_updated = queryset.update(status=1)
    message_bit = u"%s篇日志被列为删除状态" % rows_updated
    self.message_user(request,      message_bit)
    
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'update_time']
    ordering = ['title']
    actions = [make_publish, make_private, make_draft, make_trash]
    
    class Media:
        js = (
              settings.MEDIA_URL + 'tiny_mce/tiny_mce.js',
              settings.MEDIA_URL + 'textarea.js',)

    

admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(Post, PostAdmin)
