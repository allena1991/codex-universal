class Component extends DCLogic {
  state = { showOwners: null };

  source() {
    return [
      { rank: '01', title: 'Streaming template compiler', owner: 'Priya', state: 'shipped' },
      { rank: '02', title: 'Pseudo-state styling', owner: 'Marcus', state: 'shipped' },
      { rank: '03', title: 'Child component mounts', owner: 'Ana', state: 'review' },
      { rank: '04', title: 'Props and tweak metadata', owner: 'Ravi', state: 'blocked' }
    ];
  }

  renderVals() {
    const showOwners = this.state.showOwners ?? (this.props.showOwners ?? true);
    const rows = this.source().map(item => ({
      rank: item.rank,
      title: item.title,
      owner: item.owner,
      isShipped: item.state === 'shipped',
      isReview: item.state === 'review',
      isBlocked: item.state === 'blocked'
    }));
    if (this.props.blockedFirst) {
      rows.sort((a, b) => Number(b.isBlocked) - Number(a.isBlocked));
    }
    const shipped = rows.filter(r => r.isShipped).length;
    const blocked = rows.filter(r => r.isBlocked).length;
    return {
      items: rows,
      showOwners,
      readyLabel: shipped + '/' + rows.length + ' ready',
      blockedNote: blocked ? blocked + ' item blocked on review' : 'Nothing blocked',
      ownerButtonLabel: showOwners ? 'Hide owners' : 'Show owners',
      toggleOwners: () => this.setState(s => ({
        showOwners: !(s.showOwners ?? (this.props.showOwners ?? true))
      }))
    };
  }
}
