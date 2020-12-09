import React from 'react';
import { withStyles } from '@material-ui/core/styles';
import SwipeableViews from 'react-swipeable-views';
import Tabs from '@material-ui/core/Tabs';
import Tab from '@material-ui/core/Tab';
import Grid from '@material-ui/core/Grid';

import BookList from "../BookList"
import APIClient from '../apiClient'

const styles = theme => ({
  root: {
    flexGrow: 1,
    marginTop: 30
  },
  paper: {
    padding: theme.spacing(2),
    textAlign: 'center',
    color: theme.palette.text.secondary,
  },
});

class Home extends React.Component {
  state = {
    value: 0,
    books: [],
    authors: [],
    publishers: [],
    editions: []
  };

  async componentDidMount() {
    const accessToken = ""; // await this.props.authService.getAccessToken()
    this.apiClient = new APIClient(accessToken);
    this.apiClient.getBooks().then((data) =>
      this.setState({...this.state, books: data})
    );
  }

  handleTabChange = (event, value) => {
    this.setState({ value });
  };

  handleTabChangeIndex = index => {
    this.setState({ value: index });
  };

  resetBooks = books => this.setState({ ...this.state, books })

  isBook = book => this.state.books.find(b => b.id === book.id)
    onBook = (book) => {
      this.updateBackend(book);
  }

  updateBackend = (book) => {
    if (this.isBook(book)) {
      this.apiClient.deleteBook(book);
    } else {
      this.apiClient.createBook(book);
    }
    this.updateState(book);
  }

  updateState = (book) => {
    if (this.isBook(book)) {
      this.setState({
        ...this.state,
        books: this.state.books.filter(b => b.id !== book.id )
      })
    } else {
      this.setState({
        ...this.state,
        books: [book, ...this.state.books]
      })
    }
  }

  onSearch = (event) => {
    const target = event.target;
    if (!target.value || target.length < 3) { return }
    if (event.which !== 13) { return }

    APIClient(target.value)
      .then((response) => {
        target.blur();
        this.setState({ ...this.state, value: 1 });
        this.resetBooks(response.items);
      })
  }
  
  renderBooks = (books) => {
    if (!books) { return [] }
    return books.map((book) => {
      return (
        <Grid item xs={12} md={3} key={book.id}>
          <BookList onBook={this.onBook} isBook={this.isBook(book)} book={book} />
        </Grid>
      );
    })
  }

  render() {
    return (
      <div className={styles.root}>
        <Tabs
          value={this.state.value}
          onChange={this.handleTabChange}
          indicatorColor="primary"
          textColor="primary"
          variant="fullWidth"
        >
          <Tab label="Books" />
          <Tab label="Authors" />
          <Tab label="Publishers" />
        </Tabs>
      
        <SwipeableViews
          axis={'x-reverse'}
          index={this.state.value}
          onChangeIndex={this.handleTabChangeIndex}
        >
          <Grid container style={{padding: '20px 0'}}>
            { this.renderBooks(this.state.Books) }
          </Grid>
        </SwipeableViews>
      </div>
    );
  }
}

export default withStyles(styles)(Home);