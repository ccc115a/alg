import sympy as sm
import sympy.physics.mechanics as me
import sympy.physics.biomechanics as bm
import numpy as np
from scipy.optimize import fsolve
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt

# --- Define Variables ---
q1, q2, q3, q4 = me.dynamicsymbols('q1, q2, q3, q4', real=True)
u1, u2, u3, u4 = me.dynamicsymbols('u1, u2, u3, u4', real=True)
dx, dy, dz = sm.symbols('dx, dy, dz', real=True, nonnegative=True)
lA, lC, lD = sm.symbols('lA, lC, lD', real=True, positive=True)
mA, mC, mD = sm.symbols('mA, mC, mD', real=True, positive=True)
g, k, c, r = sm.symbols('g, k, c, r', real=True, positive=True)

# --- Define Kinematics ---
N, A, B, C, D = sm.symbols('N, A, B, C, D', cls=me.ReferenceFrame)
O, P1, P2, P3, P4 = sm.symbols('O, P1, P2, P3, P4 ', cls=me.Point)
Ao, Co, Cm, Dm, Do = sm.symbols('Ao, Co, Cm, Dm, Do', cls=me.Point)

A.orient_axis(N, q1, N.z)
B.orient_axis(N, q2, N.y)
C.orient_axis(B, q3, B.z)
D.orient_axis(C, q4, C.y)
A.set_ang_vel(N, u1*N.z)
B.set_ang_vel(N, u2*N.y)
C.set_ang_vel(B, u3*B.z)
D.set_ang_vel(C, u4*C.y)

Ao.set_pos(O, dx*N.x)
P1.set_pos(Ao, lA*A.y)
P2.set_pos(O, dy*N.y + dz*N.z)
Co.set_pos(P2, lC/2*C.z)
Cm.set_pos(P2, 1*lC/3*C.z)
P3.set_pos(P2, lC*C.z)
Dm.set_pos(P3, 1*lD/3*D.z)
Do.set_pos(P3, lD/2*D.z)
P4.set_pos(P3, lD*D.z)

O.set_vel(N, 0)
Ao.set_vel(N, 0)
P1.v2pt_theory(Ao, N, A)
P2.set_vel(N, 0)
Co.v2pt_theory(P2, N, C)
Cm.v2pt_theory(P2, N, C)
P3.v2pt_theory(P2, N, C)
Dm.v2pt_theory(P3, N, D)
Do.v2pt_theory(P3, N, D)
P4.v2pt_theory(P3, N, D)

# Holonomic constraint to keep hand (P4) on lever (P1)
holonomic = (P4.pos_from(O) - P1.pos_from(O)).to_matrix(N)

# --- Define Inertia ---
IA = me.Inertia(me.inertia(A, mA/12*lA**2, mA/2*lA**2, mA/12*lA**2), Ao)
IC = me.Inertia(me.inertia(C, mC/12*lC**2, mC/12*lC**2, mC/2*lC**2), Co)
ID = me.Inertia(me.inertia(D, mD/12*lD**2, mD/12*lD**2, mD/2*lD**2), Do)

lever = me.RigidBody('lever', masscenter=Ao, frame=A, mass=mA, inertia=IA)
u_arm = me.RigidBody('upper arm', masscenter=Co, frame=C, mass=mC, inertia=IC)
l_arm = me.RigidBody('lower arm', masscenter=Do, frame=D, mass=mD, inertia=ID)

# --- Define Forces ---
gravC = me.Force(u_arm, mC*g*N.z)
gravD = me.Force(l_arm, mD*g*N.z)
lever_resistance = me.Torque(A, (-k*q1 - c*u1)*N.z)

# --- Biceps Model ---
biceps_pathway = me.LinearPathway(Cm, Dm)
biceps_activation = bm.FirstOrderActivationDeGroote2016.with_defaults('biceps')
biceps = bm.MusculotendonDeGroote2016.with_defaults('biceps', biceps_pathway, biceps_activation)

# --- Triceps Model (Custom Pathway) ---
class ExtensorPathway(me.PathwayBase):
    def __init__(self, origin, insertion, axis_point, axis, parent_axis,
                 child_axis, radius, coordinate):
        super().__init__(origin, insertion)
        self.origin = origin
        self.insertion = insertion
        self.axis_point = axis_point
        self.axis = axis.normalize()
        self.parent_axis = parent_axis.normalize()
        self.child_axis = child_axis.normalize()
        self.radius = radius
        self.coordinate = coordinate

        self.origin_distance = axis_point.pos_from(origin).magnitude()
        self.insertion_distance = axis_point.pos_from(insertion).magnitude()
        self.origin_angle = sm.asin(self.radius/self.origin_distance)
        self.insertion_angle = sm.asin(self.radius/self.insertion_distance)

    @property
    def length(self):
        angle = self.origin_angle + self.coordinate + self.insertion_angle
        arc_length = self.radius*angle
        origin_segment_length = self.origin_distance*sm.cos(self.origin_angle)
        insertion_segment_length = self.insertion_distance*sm.cos(self.insertion_angle)
        return origin_segment_length + arc_length + insertion_segment_length

    @property
    def extension_velocity(self):
        return self.radius*self.coordinate.diff(me.dynamicsymbols._t)

    def to_loads(self, force_magnitude):
        parent_tangency_point = me.Point('Aw')  # fixed in parent
        child_tangency_point = me.Point('Bw')  # fixed in child

        parent_tangency_point.set_pos(
            self.axis_point,
            -self.radius*sm.cos(self.origin_angle)*self.parent_axis.cross(self.axis)
            + self.radius*sm.sin(self.origin_angle)*self.parent_axis,
        )
        child_tangency_point.set_pos(
            self.axis_point,
            self.radius*sm.cos(self.insertion_angle)*self.child_axis.cross(self.axis)
            + self.radius*sm.sin(self.insertion_angle)*self.child_axis)

        parent_force_direction_vector = self.origin.pos_from(parent_tangency_point)
        child_force_direction_vector = self.insertion.pos_from(child_tangency_point)
        force_on_parent = force_magnitude*parent_force_direction_vector.normalize()
        force_on_child = force_magnitude*child_force_direction_vector.normalize()
        loads = [
            me.Force(self.origin, force_on_parent),
            me.Force(self.axis_point, -(force_on_parent + force_on_child)),
            me.Force(self.insertion, force_on_child),
        ]
        return loads

triceps_pathway = ExtensorPathway(Cm, Dm, P3, B.y, -C.z, D.z, r, q4)
triceps_activation = bm.FirstOrderActivationDeGroote2016.with_defaults('triceps')
triceps = bm.MusculotendonDeGroote2016.with_defaults('triceps', triceps_pathway, triceps_activation)

loads = biceps.to_loads() + triceps.to_loads() + [lever_resistance, gravC, gravD]

# --- Equations of Motion ---
kane = me.KanesMethod(
    N,
    (q1,),
    (u1,),
    kd_eqs=(
        u1 - q1.diff(),
        u2 - q2.diff(),
        u3 - q3.diff(),
        u4 - q4.diff(),
    ),
    q_dependent=(q2, q3, q4),
    configuration_constraints=holonomic,
    velocity_constraints=holonomic.diff(me.dynamicsymbols._t),
    u_dependent=(u2, u3, u4),
)

Fr, Frs = kane.kanes_equations((lever, u_arm, l_arm), loads)
dadt = biceps.rhs().col_join(triceps.rhs())

# --- Evaluation Setup ---
q, u = kane.q, kane.u
a = biceps.x.col_join(triceps.x)
x = q.col_join(u).col_join(a)
e = biceps.r.col_join(triceps.r)

p = sm.Matrix([
    dx, dy, dz, lA, lC, lD, mA, mC, mD, g, k, c, r,
    biceps.F_M_max, biceps.l_M_opt, biceps.l_T_slack,
    triceps.F_M_max, triceps.l_M_opt, triceps.l_T_slack,
])

eval_diffeq = sm.lambdify((q, u, a, e, p),
                          (kane.mass_matrix, kane.forcing, dadt), cse=True)
eval_holonomic = sm.lambdify((q, p), holonomic, cse=True)

# Numerical Parameters
p_vals = np.array([
    0.31, 0.15, -0.31, 0.2, 0.3, 0.3, 1.0, 2.3, 1.7, 9.81, 5.0, 0.5, 0.03,
    500.0, 0.6*0.3, 0.55*0.3, 500.0, 0.6*0.3, 0.65*0.3,
])

# Solve for initial configuration
q_vals = np.array([
    np.deg2rad(5.0),  # q1 [rad]
    np.deg2rad(-10.0),  # q2 [rad]
    np.deg2rad(0.0),  # q3 [rad]
    np.deg2rad(75.0),  # q4 [rad]
])

def eval_holo_fsolve(x):
    q1 = q_vals[0]
    q2, q3, q4 = x
    return eval_holonomic((q1, q2, q3, q4), p_vals).squeeze()

q_vals[1:] = fsolve(eval_holo_fsolve, q_vals[1:])

u_vals = np.array([0.0, 0.0, 0.0, 0.0])
a_vals = np.array([0.0, 0.0])

# --- Simulation Function ---
def eval_r(t):
    """Returns the muscles' excitation as a function of time."""
    # Active simulation: excite biceps between 0.5s and 1.5s
    if t < 0.5 or t > 1.5:
        e = np.array([0.0, 0.0])
    else:
        e = np.array([0.8, 0.0])
    return e

def eval_rhs(t, x, r, p):
    q = x[0:4]
    u = x[4:8]
    a = x[8:10]
    e = r(t)
    
    # Solve system
    m, f, ad = eval_diffeq(q, u, a, e, p)
    ud = np.linalg.solve(m, f).squeeze()
    
    return np.hstack((u, ud, ad.squeeze()))

# --- Run Simulation ---
t0, tf = 0.0, 3.0
ts = np.linspace(t0, tf, num=301)
x0 = np.hstack((q_vals, u_vals, a_vals))

sol = solve_ivp(lambda t, x: eval_rhs(t, x, eval_r, p_vals),
                (t0, tf), x0, t_eval=ts)

# --- Plotting ---
def plot_traj(t, x, syms):
    fig, axes = plt.subplots(5, 2, sharex=True, figsize=(10, 10))
    for ax, traj, sym in zip(axes.T.flatten(), x.T, syms):
        if not sym.name.startswith('a'):
            traj = np.rad2deg(traj)
        ax.plot(t, traj)
        ax.set_ylabel(sm.latex(sym, mode='inline'))
    
    for ax in axes[-1, :]:
        ax.set_xlabel('Time [s]')
    
    fig.tight_layout()
    return axes

plot_traj(ts, sol.y.T, x)
plt.show()