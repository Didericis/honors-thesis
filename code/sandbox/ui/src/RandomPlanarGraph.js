import React, { Component } from 'react';
import { UncontrolledReactSVGPanZoom } from 'react-svg-pan-zoom';
import { SvgLoader } from 'react-svgmt'
import $ from 'jquery';
import ReactJson from 'react-json-view'

import * as api from './api';

export default class RandomPlanarGraph extends Component {
  Viewer = null

  MODES = ['color', 'strip', 'reverseStrip']

  constructor(props) {
    super(props)
    this.getUrl = this.getUrl.bind(this);
    this.createNewGraph = this.createNewGraph.bind(this);
    this.registerClickHandlers = this.registerClickHandlers.bind(this);
    this.setNumPointsInNewGraph = this.setNumPointsInNewGraph.bind(this);
    this.toggleMode = this.toggleMode.bind(this);
  }

  state = {
    selectedColor: 'red',
    coloredNodes: {},
    graphs: [],
    seed: null,
    numPointsInNewGraph: 200,
    sliceOrigin: null,
    mode: this.MODES[0],
    graphData: null,
  }

  componentDidMount() {
    this.getGraphs();
  }

  componentDidUpdate(prevProps, prevState) {
    if (this.state.seed && (prevState.seed !== this.state.seed)) {
      this.getGraphs();
      this.getGraphData(this.state.seed).then(graphData => {
        this.setState({ graphData });
      });
    }
  }

  createNewGraph() {
    this.setState({ seed: this.generateSeed() });
  }

  setNumPointsInNewGraph(e) {
    this.setState({ numPointsInNewGraph: e.target.value });
  }

  generateSeed() {
    return String(Math.random() * Math.pow(10, 17));
  }

  getUrl() {
    const { seed, sliceOrigin, colors, numPointsInNewGraph, mode } = this.state;
    let url = api.url + `/planar-graphs/${seed}/graph.svg`;
    const query = [];
    if (sliceOrigin) query.push(`slice-origin-id=${sliceOrigin}`);
    if (mode === 'reverseStrip') query.push('reverse-slice=True');
    if (numPointsInNewGraph) query.push(`num-points=${numPointsInNewGraph}`);
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

  getGraphData(seed) {
    return fetch(api.url + `/planar-graphs/${seed}/graph.json`).then(data => data.json());
  }

  render() {
    const { mode, seed, numPointsInNewGraph, selectedColor, graphData } = this.state;
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
            <label>Points in new graph:</label>
            <input value={numPointsInNewGraph} onChange={this.setNumPointsInNewGraph} />
            <button onClick={this.createNewGraph}>Create Graph</button>
          </div>
          <div className='row'>
            <button onClick={this.toggleMode}>Mode: {mode}</button>
            <button style={{ backgroundColor: 'blue' }} onClick={this.selectColor.bind(this, 'blue')}>Blue</button>
            <button style={{ backgroundColor: 'red' }} onClick={this.selectColor.bind(this, 'red')}>Red</button>
            <button style={{ backgroundColor: 'yellow' }} onClick={this.selectColor.bind(this, 'yellow')}>Yellow</button>
            <button style={{ backgroundColor: 'green' }} onClick={this.selectColor.bind(this, 'green')}>Green</button>
            <button style={{ backgroundColor: 'white' }} onClick={this.selectColor.bind(this, 'white')}>White</button>
            <span style={{ color: selectedColor }}>Selected: { selectedColor }</span>
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
        <div className='column'>
          <ReactJson src={graphData} collapsed={true} theme='monokai' style={{ maxHeight: '80vh', overflow: 'scroll', border: '1px solid white'}} />
        </div>
      </div>
    );
  }
}
