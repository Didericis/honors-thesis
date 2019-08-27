import React, { Component } from 'react';
import { UncontrolledReactSVGPanZoom } from 'react-svg-pan-zoom';
import { SvgLoader } from 'react-svgmt'
import $ from 'jquery';

import * as api from './api';

export default class RandomPlanarGraph extends Component {
  Viewer = null

  MODES = ['color', 'strip', 'reverseStrip']

  constructor(props) {
    super(props)
    this.getUrl = this.getUrl.bind(this);
    this.createNewGraph = this.createNewGraph.bind(this);
    this.registerClickHandlers = this.registerClickHandlers.bind(this);
    this.toggleMode = this.toggleMode.bind(this);
  }

  state = {
    selectedColor: 'red',
    coloredNodes: {},
    graphs: [],
    seed: null,
    sliceOrigin: null,
    mode: this.MODES[0]
  }

  componentDidMount() {
    this.getGraphs();
  }

  componentDidUpdate(prevProps, prevState) {
    if (prevState.seed && (prevState.seed !== this.state.seed)) {
      this.getGraphs();
    }
  }

  createNewGraph() {
    this.setState({ seed: this.generateSeed() });
  }

  generateSeed() {
    return String(Math.random() * Math.pow(10, 17));
  }

  getUrl() {
    const { seed, sliceOrigin, colors, mode } = this.state;
    let url = api.url + `/planar-graphs/${seed}/graph.svg`;
    const query = [];
    if (sliceOrigin) query.push(`slice-origin-id=${sliceOrigin}`);
    if (mode === 'reverseStrip') query.push('reverse-slice=True');
    if (colors) {
      Object.keys(colors).forEach((id) => {
        query.push(`${id}=${colors[id]}`);
      });
    }
    if (query.length) url += '?' + query.join('&')
    return url;
  }

  getGraphs() {
    return fetch(api.url + '/planar-graphs').then(
      res => res.json()
    ).then(graphs => {
      const newState = { graphs };
      if (!this.state.seed && graphs.length) {
        newState.seed = graphs[0];
      }
      this.setState(newState);
      return graphs;
    });
  }

  onClickNode(e) {
    const { mode, selectedColor } = this.state;
    const id = $(e.target).attr('id');
    if (['strip', 'reverseStrip'].includes(mode)) {
      const sliceOrigin = id;
      this.setState({ sliceOrigin });
    } else if (mode === 'color') {
      this.setState(({ colors }) => ({
        colors: { ...colors, [id]: selectedColor }
      }));
    }
  }

  registerClickHandlers() {
    $('.node').on('click', (e) => {
      this.onClickNode(e);
    });
  }

  onClickSeed(seed) {
    this.setState({ seed, sliceOrigin: null })
  }

  onClickDelete(seed) {
    return fetch(api.url + `/planar-graphs/${seed}`, { method: 'DELETE' }).then(() => {
      return this.getGraphs().then(graphs => {
        if (graphs.length && (seed === this.state.seed)) {
          this.setState({ seed: graphs[0] });
        }
      });
    });
  }

  clearColors() {
    this.setState({ colors: {} });
  }

  selectColor(selectedColor) {
    this.setState({ selectedColor });
  }

  toggleMode() {
    const { MODES } = this;
    const { mode } = this.state;
    this.setState({
      mode: MODES[(MODES.indexOf(mode) + 1) % MODES.length]
    });
  }

  render() {
    const { mode, seed, selectedColor } = this.state;
    return (
      <div className='row'>
        <div className='column'>
          {
            this.state.graphs.map(id => (
              <div key={id} className='row'>
                <button onClick={() => this.onClickDelete(id)}>X</button>
                <button
                  onClick={() => this.onClickSeed(id)}
                  className={id === this.state.seed ? 'active' : ''}>
                    {id}
                </button>
              </div>
            ))
          }
        </div>
        <div className='column'>
          <div className='row'>
            <button onClick={this.createNewGraph}>Regenerate</button>
            <button style={{ backgroundColor: 'blue' }} onClick={this.selectColor.bind(this, 'blue')}>Blue</button>
            <button style={{ backgroundColor: 'red' }} onClick={this.selectColor.bind(this, 'red')}>Red</button>
            <button style={{ backgroundColor: 'yellow' }} onClick={this.selectColor.bind(this, 'yellow')}>Yellow</button>
            <button style={{ backgroundColor: 'green' }} onClick={this.selectColor.bind(this, 'green')}>Green</button>
            <button style={{ backgroundColor: 'white' }} onClick={this.selectColor.bind(this, 'white')}>White</button>
            <span style={{ color: selectedColor }}>Selected: { selectedColor }</span>
            <button onClick={this.toggleMode}>Mode: {mode}</button>
          </div>
          <div className='row'>
            <UncontrolledReactSVGPanZoom
              tool='auto'
              className='svg-viewer'
              width={1500} height={1000}
              ref={Viewer => this.Viewer = Viewer}
              SVGBackground='transparent'
              background='transparent'>
              <svg width={1500} height={1000}>
                { seed && <SvgLoader path={this.getUrl()} onSVGReady={this.registerClickHandlers} /> }
              </svg>
            </UncontrolledReactSVGPanZoom>
          </div>
        </div>
      </div>
    );
  }
}
