/* Generated by GOB (v2.0.14)   (do not edit directly) */

#include <glib.h>
#include <glib-object.h>
#ifndef __SACAM_POINT_H__
#define __SACAM_POINT_H__

#ifdef __cplusplus
extern "C" {
#endif /* __cplusplus */


/*
 * Type checking and casting macros
 */
#define SACAM_TYPE_POINT	(sacam_point_get_type())
#define SACAM_POINT(obj)	G_TYPE_CHECK_INSTANCE_CAST((obj), sacam_point_get_type(), SacamPoint)
#define SACAM_POINT_CONST(obj)	G_TYPE_CHECK_INSTANCE_CAST((obj), sacam_point_get_type(), SacamPoint const)
#define SACAM_POINT_CLASS(klass)	G_TYPE_CHECK_CLASS_CAST((klass), sacam_point_get_type(), SacamPointClass)
#define SACAM_IS_POINT(obj)	G_TYPE_CHECK_INSTANCE_TYPE((obj), sacam_point_get_type ())

#define SACAM_POINT_GET_CLASS(obj)	G_TYPE_INSTANCE_GET_CLASS((obj), sacam_point_get_type(), SacamPointClass)

/*
 * Main object structure
 */
#ifndef __TYPEDEF_SACAM_POINT__
#define __TYPEDEF_SACAM_POINT__
typedef struct _SacamPoint SacamPoint;
#endif
struct _SacamPoint {
	GObject __parent__;
	/*< public >*/
	gchar * start;
	gchar * end;
	gint x_pos;
	gint y_pos;
};

/*
 * Class definition
 */
typedef struct _SacamPointClass SacamPointClass;
struct _SacamPointClass {
	GObjectClass __parent__;
};


/*
 * Public methods
 */
GType	sacam_point_get_type	(void);
gchar * 	sacam_point_get_start	(SacamPoint * self);
void 	sacam_point_set_start	(SacamPoint * self,
					gchar * val);
gchar * 	sacam_point_get_end	(SacamPoint * self);
void 	sacam_point_set_end	(SacamPoint * self,
					gchar * val);
gint 	sacam_point_get_x_pos	(SacamPoint * self);
void 	sacam_point_set_x_pos	(SacamPoint * self,
					gint val);
gint 	sacam_point_get_y_pos	(SacamPoint * self);
void 	sacam_point_set_y_pos	(SacamPoint * self,
					gint val);
GObject * 	sacam_point_new	(void);
GObject * 	sacam_point_new_from_data	(gint x,
					gint y,
					gchar * begin,
					gchar * finish);

/*
 * Argument wrapping macros
 */
#if defined(__GNUC__) && !defined(__STRICT_ANSI__)
#define SACAM_POINT_PROP_START(arg)    	"start", __extension__ ({gchar *z = (arg); z;})
#define SACAM_POINT_GET_PROP_START(arg)	"start", __extension__ ({gchar **z = (arg); z;})
#define SACAM_POINT_PROP_END(arg)    	"end", __extension__ ({gchar *z = (arg); z;})
#define SACAM_POINT_GET_PROP_END(arg)	"end", __extension__ ({gchar **z = (arg); z;})
#define SACAM_POINT_PROP_X_POS(arg)    	"x_pos", __extension__ ({gint z = (arg); z;})
#define SACAM_POINT_GET_PROP_X_POS(arg)	"x_pos", __extension__ ({gint *z = (arg); z;})
#define SACAM_POINT_PROP_Y_POS(arg)    	"y_pos", __extension__ ({gint z = (arg); z;})
#define SACAM_POINT_GET_PROP_Y_POS(arg)	"y_pos", __extension__ ({gint *z = (arg); z;})
#else /* __GNUC__ && !__STRICT_ANSI__ */
#define SACAM_POINT_PROP_START(arg)    	"start",(gchar *)(arg)
#define SACAM_POINT_GET_PROP_START(arg)	"start",(gchar **)(arg)
#define SACAM_POINT_PROP_END(arg)    	"end",(gchar *)(arg)
#define SACAM_POINT_GET_PROP_END(arg)	"end",(gchar **)(arg)
#define SACAM_POINT_PROP_X_POS(arg)    	"x_pos",(gint )(arg)
#define SACAM_POINT_GET_PROP_X_POS(arg)	"x_pos",(gint *)(arg)
#define SACAM_POINT_PROP_Y_POS(arg)    	"y_pos",(gint )(arg)
#define SACAM_POINT_GET_PROP_Y_POS(arg)	"y_pos",(gint *)(arg)
#endif /* __GNUC__ && !__STRICT_ANSI__ */


#ifdef __cplusplus
}
#endif /* __cplusplus */

#endif
