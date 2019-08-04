import React, { Component } from 'react';
import { UncontrolledReactSVGPanZoom } from 'react-svg-pan-zoom';
import { SvgLoader } from 'react-svgmt'
import $ from 'jquery';

import * as api from './api';

export default class RandomPlanarGraph extends Component {
  Viewer = null

  constructor(props) {
    super(props)
    this.getUrl = this.getUrl.bind(this);
    this.regenerate = this.regenerate.bind(this);
    this.registerClickHandlers = this.registerClickHandlers.bind(this);
    this.startRotation = this.startRotation.bind(this);
  }

  state = {
    graphs: [],
    seed: null,
    sliceOrigin: null,
    mode: 'rotationA'
  }

  componentDidMount() {
    this.getGraphs();
  }

  componentDidUpdate(prevProps, prevState) {
    if (prevState.seed && (prevState.seed !== this.state.seed)) {
      this.getGraphs();
    }
  }

  regenerate() {
    this.setState({ seed: this.generateSeed() });
  }

  generateSeed() {
    return String(Math.random() * Math.pow(10, 17));
  }

  getUrl() {
    const { seed, sliceOrigin, rotationA, rotationB } = this.state;
    let url = api.url + `/planar-graphs/${seed}/graph.svg`;
    const query = [];
    if (sliceOrigin) query.push(`slice-origin-id=${sliceOrigin}`);
    if (rotationA && rotationB) {
      query.push(`rotationA=${rotationA}`);
      query.push(`rotationB=${rotationB}`);
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
    const { mode } = this.state;
    const id = $(e.target).attr('id');
    if (mode === 'strip') {
      const sliceOrigin = id;
      this.setState({ sliceOrigin });
    } else if (mode === 'rotationA') {
      this.setState({
        rotationA: id,
        rotationB: null,
      });
      setTimeout(() => {
        this.setState({ mode: 'rotationB' });
      }, 1000);
    } else {
      this.setState({ rotationB: id });
      setTimeout(() => {
        this.setState({ mode: 'rotationA' });
      }, 1000);
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

  startRotation() {
    this.setState({
      mode: 'rotationA',
      rotationA: null,
      rotationB: null,
    });
  }

  render() {
    const { seed, mode } = this.state;
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
            <button onClick={this.regenerate}>Regenerate</button>
            <button onClick={this.startRotation}>Start Rotation</button>
            <span>{mode}</span>
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
