# -*- encoding: utf-8 -*-
"""
A plotting function to plot a specific soccer scene.
"""
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np
import copy


colors = ['r','b']

def circle(x0,y0,r):
    """Calculates the x-y-coordinates for a circle at x0,y0 with radius R.

    Args:
        x0: x-coordinate circle center
        y0: y-coordinate circle center
        r: radis of circle
    Returns:
        List with x and y values.
    """
    t = np.arange(0,np.pi*2.0,0.01)
    x = x0 + r * np.sin(t)
    y = y0 + r * np.cos(t)
    return [x,y]

def determine_ball_impacts(ball):
    ball_acc = np.sqrt(np.sum(np.diff(ball,2,0)**2,axis=1))
    return np.where(ball_acc>0.01)

def plot_stadium(width, length):
    """ Plots a canonical stadium.

    Plots a given stadium according to the width and length specs and the
    FIFA rules for goals etc. in scale. Depends on the circle function to 
    draw the center circle.

    Args:
        width: total width of the stadium in meters.
        length: total length of the stadium in meters.

    Returns: None
    """
    w = width / 2.0
    l = length / 2.0
    current_axis = plt.gca()
    current_axis.add_patch(Rectangle((-l,-w), 2.0*l, 2.0*w, facecolor='#00FF00'))
    plt.plot([-l, l, l, -l, -l], [-w, -w, w, w, -w], 'k-', lw=2)
    plt.plot([0, 0], [-w, w], 'k-', lw=2)
    [mx,my] = circle(0, 0, 9.15)
    plt.plot(mx, my,'k-',lw=2)
    plt.plot([-l, -l+5.5, -l+5.5, -l], [9.16, 9.16, -9.16, -9.16],'k-',lw=2)
    plt.plot([-l, -l+16.5, -l+16.5,-l],[20.16,20.16,-20.16,-20.16],'k-',lw=2)
    plt.plot([l, l-5.5, l-5.5, l],[9.16,9.16,-9.16,-9.16],'k-',lw=2)
    plt.plot([l, l-16.5, l-16.5, l],[20.16,20.16,-20.16,-20.16],'k-',lw=2)

def plot_players(pos_data,frames):
    """
    """
    for i,team in enumerate(['home','guest']):
        for player in pos_data[team]:
            idx = np.logical_and(player[1][:,0] >= frames[0],
                    player[1][:,0] <= frames[-1])
            if np.sum(idx) == frames.size:
                idxf = np.where(idx)
                plt.plot(player[1][idx,1],
                        player[1][idx,2],
                        colors[i],alpha=.8)
                plt.plot(player[1][idxf[0][0],1],
                        player[1][idxf[0][0],2],
                            color=colors[i], marker='o', markersize=8,
                            alpha=.5)
                plt.plot(player[1][idxf[0][-1],1],
                        player[1][idxf[0][-1],2],
                            color=colors[i], marker='o', markersize=8)
                plt.text(player[1][idxf[0][0],1],
                        player[1][idxf[0][0],2],
                        player[0])

def plot_ball(ball_data,frames):
    """
    """
    plt.plot(ball_data[frames,1], ball_data[frames,2],'k',lw=2)
    plt.plot(ball_data[-1,1],ball_data[-1,2],'ko')

def rescale_data(pos, ball, stadium):
    """

    In place rescaling of position data.

    Args:
    Returns: Null
    """
    w = stadium['width']/2.0
    l = stadium['length']/2.0
    for role in pos.keys():
        for player in pos[role]:
            player[1][:,1] *= l
            player[1][:,2] *= w
    ball[:,1] *= l
    ball[:,2] *= w


def plot(pos, ball, stadium, frames, rescale=False ):
    """Convenience function to plot a soccer scene.

    Depends on the matplotlib library.

    Args:
        pos: position data of the player following the convention:

        stadium: width and length dictionary.
        pts_range: range of frames to be drawn.

    Returns: None
    """
    plot_stadium(**stadium)

    if rescale:
        rescale_data(pos, ball, stadium)

    plot_players(pos,frames)
    plot_ball(ball,frames)

    # final plot adjustments
    plt.axes().set_aspect('equal','datalim')
    plt.axis('off')
    plt.show()

if __name__ == '__main__':
    mm = copy.deepcopy(dict(home=pos_data['home']['1st'],
        guest=pos_data['guest']['1st']))
    bb = copy.deepcopy(ball_data[0])
    # tagged shot time = 14275
    #frames = np.arange(14125,14300)
    # tagged two 17850
    frames = np.arange(tag-200,tag+200)
    plot(mm,bb,{'length':105,'width':68},frames=frames,rescale=True)
    sh = mm['guest'][3][1][frames,:]
    sh_b = bb[frames,1:3]
    dd = sh[:,1:3] - sh_b
    dd1 = np.sqrt(np.sum(dd**2,axis=1))
