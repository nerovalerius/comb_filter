def pzmap(G, ax=None, marker_color = None):
    
    if marker_color:
        marker_color = [marker_color, marker_color]
    else:
        marker_color = ["r", "b"]
            
    
    if ax:
        actual_imag_min, actual_imag_max = ax.get_ylim()
        actual_real_min, actual_real_max = ax.get_xlim()
    else:
        _, ax = plt.subplots(figsize=(5, 5))
    
    if ax.lines == []:
        # circle
        theta = np.linspace(-np.pi, np.pi, 201)
        ax.plot(np.sin(theta), np.cos(theta), color = 'k', linewidth=0.5)
        ax.axhline(y=0, color='k', alpha=0.3)
        ax.axvline(x=0, color='k', alpha=0.3) 
        actual_imag_min, actual_imag_max = -1.0, 1.0
        actual_real_min, actual_real_max = -1.0, 1.0
       
    # poles
    ax.plot(np.real(G.poles), np.imag(G.poles), 'X%s' % marker_color[0], label = 'Poles')

    # zeros
    ax.plot(np.real(G.zeros), np.imag(G.zeros), '.%s' % marker_color[1], label = 'Zeros')
    
    def make_one_long(a, b, c):
        a = np.array(a)
        gesamt = np.append(a, b)
        return np.append(gesamt, c)

    imag_min = np.min(make_one_long([actual_imag_min], np.imag(G.poles), np.imag(G.zeros))) * 1.05
    imag_max = np.max(make_one_long([actual_imag_max], np.imag(G.poles), np.imag(G.zeros))) * 1.05
    real_min = np.min(make_one_long([actual_real_min], np.real(G.poles), np.real(G.zeros))) * 1.05
    real_max = np.max(make_one_long([actual_real_max], np.real(G.poles), np.real(G.zeros))) * 1.05
    all_lim = np.max([np.abs(real_min), real_max, np.abs(imag_min), imag_max])
    ax.set_xlim(-all_lim, all_lim)
    ax.set_ylim(-all_lim, all_lim) 
        
    ax.legend(loc=1)
    ax.grid()
    return ax
