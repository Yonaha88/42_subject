/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_printf2.c                                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: kyonaha <kyonaha@student.42tokyo.jp>       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/05/17 11:19:37 by hkanamit          #+#    #+#             */
/*   Updated: 2026/05/18 13:27:12 by kyonaha          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

void	put_char(char c, int *ret)
{
	if (write(2, &c, 1) == 1)
		*ret += 1;
	else
		*ret = -1;
}

void	putstr(char *s, int *ret)
{
	int	i;

	i = 0;
	if (s == NULL)
	{
		if (write(2, "(null)", 6) == 6)
			*ret += 6;
		else
			*ret = -1;
		return ;
	}
	while (s[i])
	{
		if (write(2, &s[i], 1) == 1)
			*ret += 1;
		else
		{
			*ret = -1;
			return ;
		}
		i++;
	}
}

static void	put_nbr_2(int nbr, int *ret)
{
	if (nbr == -2147483648)
	{
		if (write(2, "-2147483648", 11) == 11)
		{
			*ret += 11;
			return ;
		}
		else
		{
			*ret = -1;
			return ;
		}
	}
}

static void	put_nbr3(int nbr, int *ret)
{
	char	c;

	c = nbr % 10 + '0';
	if (write(2, &c, 1) == 1)
		*ret += 1;
	else
	{
		*ret = -1;
		return ;
	}
}

void	put_nbr(int nbr, int *ret)
{
	if (nbr == -2147483648)
	{
		put_nbr_2(nbr, ret);
		return ;
	}
	if (nbr < 0)
	{
		if (write(2, "-", 1) == 1)
			*ret += 1;
		else
		{
			*ret = -1;
			return ;
		}
		nbr = -nbr;
	}
	if (nbr >= 10)
		put_nbr(nbr / 10, ret);
	if (*ret == -1)
		return ;
	put_nbr3(nbr, ret);
	if (*ret == -1)
		return ;
}
