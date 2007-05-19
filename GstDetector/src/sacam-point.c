/* Generated by GOB (v2.0.14)   (do not edit directly) */

/* End world hunger, donate to the World Food Programme, http://www.wfp.org */

#define GOB_VERSION_MAJOR 2
#define GOB_VERSION_MINOR 0
#define GOB_VERSION_PATCHLEVEL 14

#define selfp (self->_priv)

#include <string.h> /* memset() */

#ifdef G_LIKELY
#define ___GOB_LIKELY(expr) G_LIKELY(expr)
#define ___GOB_UNLIKELY(expr) G_UNLIKELY(expr)
#else /* ! G_LIKELY */
#define ___GOB_LIKELY(expr) (expr)
#define ___GOB_UNLIKELY(expr) (expr)
#endif /* G_LIKELY */


#include "sacam-point.h"
#include "sacam-point-private.h"

/* self casting macros */
#define SELF(x) SACAM_POINT(x)
#define SELF_CONST(x) SACAM_POINT_CONST(x)
#define IS_SELF(x) SACAM_IS_POINT(x)
#define TYPE_SELF SACAM_TYPE_POINT
#define SELF_CLASS(x) SACAM_POINT_CLASS(x)

#define SELF_GET_CLASS(x) SACAM_POINT_GET_CLASS(x)

/* self typedefs */
typedef SacamPoint Self;
typedef SacamPointClass SelfClass;

/* here are local prototypes */
static void ___object_set_property (GObject *object, guint property_id, const GValue *value, GParamSpec *pspec);
static void ___object_get_property (GObject *object, guint property_id, GValue *value, GParamSpec *pspec);
static void sacam_point_init (SacamPoint * o) G_GNUC_UNUSED;
static void sacam_point_class_init (SacamPointClass * c) G_GNUC_UNUSED;

enum {
	PROP_0,
	PROP_START,
	PROP_END,
	PROP_X_POS,
	PROP_Y_POS
};

/* pointer to the class of our parent */
static GObjectClass *parent_class = NULL;

/* Short form macros */
#define self_get_start sacam_point_get_start
#define self_set_start sacam_point_set_start
#define self_get_end sacam_point_get_end
#define self_set_end sacam_point_set_end
#define self_get_x_pos sacam_point_get_x_pos
#define self_set_x_pos sacam_point_set_x_pos
#define self_get_y_pos sacam_point_get_y_pos
#define self_set_y_pos sacam_point_set_y_pos
#define self_new_from_data sacam_point_new_from_data
GType
sacam_point_get_type (void)
{
	static GType type = 0;

	if ___GOB_UNLIKELY(type == 0) {
		static const GTypeInfo info = {
			sizeof (SacamPointClass),
			(GBaseInitFunc) NULL,
			(GBaseFinalizeFunc) NULL,
			(GClassInitFunc) sacam_point_class_init,
			(GClassFinalizeFunc) NULL,
			NULL /* class_data */,
			sizeof (SacamPoint),
			0 /* n_preallocs */,
			(GInstanceInitFunc) sacam_point_init,
			NULL
		};

		type = g_type_register_static (G_TYPE_OBJECT, "SacamPoint", &info, (GTypeFlags)0);
	}

	return type;
}

/* a macro for creating a new object of our type */
#define GET_NEW ((SacamPoint *)g_object_new(sacam_point_get_type(), NULL))

/* a function for creating a new object of our type */
#include <stdarg.h>
static SacamPoint * GET_NEW_VARG (const char *first, ...) G_GNUC_UNUSED;
static SacamPoint *
GET_NEW_VARG (const char *first, ...)
{
	SacamPoint *ret;
	va_list ap;
	va_start (ap, first);
	ret = (SacamPoint *)g_object_new_valist (sacam_point_get_type (), first, ap);
	va_end (ap);
	return ret;
}


static void
___finalize(GObject *obj_self)
{
#define __GOB_FUNCTION__ "Sacam:Point::finalize"
	SacamPoint *self G_GNUC_UNUSED = SACAM_POINT (obj_self);
	gpointer priv G_GNUC_UNUSED = self->_priv;
	if(G_OBJECT_CLASS(parent_class)->finalize) \
		(* G_OBJECT_CLASS(parent_class)->finalize)(obj_self);
	if(self->_priv->start) { g_free ((gpointer) self->_priv->start); self->_priv->start = NULL; }
	if(self->_priv->end) { g_free ((gpointer) self->_priv->end); self->_priv->end = NULL; }
}
#undef __GOB_FUNCTION__

static void 
sacam_point_init (SacamPoint * o G_GNUC_UNUSED)
{
#define __GOB_FUNCTION__ "Sacam:Point::init"
	o->_priv = G_TYPE_INSTANCE_GET_PRIVATE(o,SACAM_TYPE_POINT,SacamPointPrivate);
}
#undef __GOB_FUNCTION__
static void 
sacam_point_class_init (SacamPointClass * c G_GNUC_UNUSED)
{
#define __GOB_FUNCTION__ "Sacam:Point::class_init"
	GObjectClass *g_object_class G_GNUC_UNUSED = (GObjectClass*) c;

	g_type_class_add_private(c,sizeof(SacamPointPrivate));

	parent_class = g_type_class_ref (G_TYPE_OBJECT);

	g_object_class->finalize = ___finalize;
	g_object_class->get_property = ___object_get_property;
	g_object_class->set_property = ___object_set_property;
    {
	GParamSpec   *param_spec;

	param_spec = g_param_spec_string
		("start" /* name */,
		 "Start" /* nick */,
		 "Initial time in this point" /* blurb */,
		 "2007-05-19T11:31:12.573" /* default_value */,
		 (GParamFlags)(G_PARAM_READABLE | G_PARAM_WRITABLE));
	g_object_class_install_property (g_object_class,
		PROP_START,
		param_spec);
	param_spec = g_param_spec_string
		("end" /* name */,
		 "End" /* nick */,
		 "Final time in this point" /* blurb */,
		 "2007-05-19T11:31:12.573" /* default_value */,
		 (GParamFlags)(G_PARAM_READABLE | G_PARAM_WRITABLE));
	g_object_class_install_property (g_object_class,
		PROP_END,
		param_spec);
	param_spec = g_param_spec_int
		("x_pos" /* name */,
		 "X Position" /* nick */,
		 "X position of the point" /* blurb */,
		 0 /* minimum */,
		 INT_MAX /* maximum */,
		 0 /* default_value */,
		 (GParamFlags)(G_PARAM_READABLE | G_PARAM_WRITABLE));
	g_object_class_install_property (g_object_class,
		PROP_X_POS,
		param_spec);
	param_spec = g_param_spec_int
		("y_pos" /* name */,
		 "Y Position" /* nick */,
		 "Y position of the point" /* blurb */,
		 0 /* minimum */,
		 INT_MAX /* maximum */,
		 0 /* default_value */,
		 (GParamFlags)(G_PARAM_READABLE | G_PARAM_WRITABLE));
	g_object_class_install_property (g_object_class,
		PROP_Y_POS,
		param_spec);
    }
}
#undef __GOB_FUNCTION__

static void
___object_set_property (GObject *object,
	guint property_id,
	const GValue *VAL G_GNUC_UNUSED,
	GParamSpec *pspec G_GNUC_UNUSED)
#define __GOB_FUNCTION__ "Sacam:Point::set_property"
{
	SacamPoint *self G_GNUC_UNUSED;

	self = SACAM_POINT (object);

	switch (property_id) {
	case PROP_START:
		{
{ char *old = self->_priv->start; self->_priv->start = g_value_dup_string (VAL); g_free (old); }
		}
		break;
	case PROP_END:
		{
{ char *old = self->_priv->end; self->_priv->end = g_value_dup_string (VAL); g_free (old); }
		}
		break;
	case PROP_X_POS:
		{
self->_priv->x_pos = g_value_get_int (VAL);
		}
		break;
	case PROP_Y_POS:
		{
self->_priv->y_pos = g_value_get_int (VAL);
		}
		break;
	default:
/* Apparently in g++ this is needed, glib is b0rk */
#ifndef __PRETTY_FUNCTION__
#  undef G_STRLOC
#  define G_STRLOC	__FILE__ ":" G_STRINGIFY (__LINE__)
#endif
		G_OBJECT_WARN_INVALID_PROPERTY_ID (object, property_id, pspec);
		break;
	}
}
#undef __GOB_FUNCTION__

static void
___object_get_property (GObject *object,
	guint property_id,
	GValue *VAL G_GNUC_UNUSED,
	GParamSpec *pspec G_GNUC_UNUSED)
#define __GOB_FUNCTION__ "Sacam:Point::get_property"
{
	SacamPoint *self G_GNUC_UNUSED;

	self = SACAM_POINT (object);

	switch (property_id) {
	case PROP_START:
		{
g_value_set_string (VAL, self->_priv->start);
		}
		break;
	case PROP_END:
		{
g_value_set_string (VAL, self->_priv->end);
		}
		break;
	case PROP_X_POS:
		{
g_value_set_int (VAL, self->_priv->x_pos);
		}
		break;
	case PROP_Y_POS:
		{
g_value_set_int (VAL, self->_priv->y_pos);
		}
		break;
	default:
/* Apparently in g++ this is needed, glib is b0rk */
#ifndef __PRETTY_FUNCTION__
#  undef G_STRLOC
#  define G_STRLOC	__FILE__ ":" G_STRINGIFY (__LINE__)
#endif
		G_OBJECT_WARN_INVALID_PROPERTY_ID (object, property_id, pspec);
		break;
	}
}
#undef __GOB_FUNCTION__



gchar * 
sacam_point_get_start (SacamPoint * self)
{
#define __GOB_FUNCTION__ "Sacam:Point::get_start"
{
		gchar* val; g_object_get (G_OBJECT (self), "start", &val, NULL); return val;
}}
#undef __GOB_FUNCTION__

void 
sacam_point_set_start (SacamPoint * self, gchar * val)
{
#define __GOB_FUNCTION__ "Sacam:Point::set_start"
{
		g_object_set (G_OBJECT (self), "start", val, NULL);
}}
#undef __GOB_FUNCTION__

gchar * 
sacam_point_get_end (SacamPoint * self)
{
#define __GOB_FUNCTION__ "Sacam:Point::get_end"
{
		gchar* val; g_object_get (G_OBJECT (self), "end", &val, NULL); return val;
}}
#undef __GOB_FUNCTION__

void 
sacam_point_set_end (SacamPoint * self, gchar * val)
{
#define __GOB_FUNCTION__ "Sacam:Point::set_end"
{
		g_object_set (G_OBJECT (self), "end", val, NULL);
}}
#undef __GOB_FUNCTION__

gint 
sacam_point_get_x_pos (SacamPoint * self)
{
#define __GOB_FUNCTION__ "Sacam:Point::get_x_pos"
{
		gint val; g_object_get (G_OBJECT (self), "x_pos", &val, NULL); return val;
}}
#undef __GOB_FUNCTION__

void 
sacam_point_set_x_pos (SacamPoint * self, gint val)
{
#define __GOB_FUNCTION__ "Sacam:Point::set_x_pos"
{
		g_object_set (G_OBJECT (self), "x_pos", val, NULL);
}}
#undef __GOB_FUNCTION__

gint 
sacam_point_get_y_pos (SacamPoint * self)
{
#define __GOB_FUNCTION__ "Sacam:Point::get_y_pos"
{
		gint val; g_object_get (G_OBJECT (self), "y_pos", &val, NULL); return val;
}}
#undef __GOB_FUNCTION__

void 
sacam_point_set_y_pos (SacamPoint * self, gint val)
{
#define __GOB_FUNCTION__ "Sacam:Point::set_y_pos"
{
		g_object_set (G_OBJECT (self), "y_pos", val, NULL);
}}
#undef __GOB_FUNCTION__

GObject * 
sacam_point_new_from_data (gint x, gint y, gchar * begin, gchar * finish)
{
#define __GOB_FUNCTION__ "Sacam:Point::new_from_data"
{
	
        GObject *obj = (GObject *)GET_NEW;
        g_object_set (G_OBJECT (obj), "x_pos", x);
        g_object_set (G_OBJECT (obj), "y_pos", y);
        g_object_set (G_OBJECT (obj), "start", g_strdup(begin));
        g_object_set (G_OBJECT (obj), "end", g_strdup(finish));

        return obj;
    }}
#undef __GOB_FUNCTION__
